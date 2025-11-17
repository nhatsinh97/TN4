// ESP32 ATS + Selec + MQTT + Web OTA qua Ethernet
#include <ModbusMaster.h>
#include <SPI.h>
#include <Ethernet.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <ESP32Ping.h>
#include <WebServer.h>
#include <Update.h>

#define MAX485_DE_RE 4
#define RXD2 16
#define TXD2 17

ModbusMaster ats1, ats2, selec1, selec2;
byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };
IPAddress mqttServer(10, 16, 40, 138);
EthernetClient ethClient;
PubSubClient mqttClient(ethClient);
WebServer server(80);

unsigned long lastPoll = 0, lastSuccessRead = 0;
const unsigned long POLL_INTERVAL = 1000, MAX_TIMEOUT = 60000;
unsigned long lastErrorGen1 = 0, lastErrorGen2 = 0, lastErrorSelec1 = 0, lastErrorSelec2 = 0;
const unsigned long errorPrintInterval = 5000;

enum CoilAddress {
  COIL_AUTO_MANUAL = 15004,
  COIL_ALARM_RESET = 15007,
  COIL_START = 15008,
  COIL_STOP = 15009,
  COIL_CLOSE_ACB = 15000,
  COIL_OPEN_ACB = 15001
};

void preTransmission() { digitalWrite(MAX485_DE_RE, HIGH); }
void postTransmission() { digitalWrite(MAX485_DE_RE, LOW); }

float toFloat(uint16_t hi, uint16_t lo) {
  union { uint32_t i; float f; } u;
  u.i = ((uint32_t)lo << 16) | hi;
  return roundf(u.f * 10) / 10.0;
}

uint16_t ModbusCRC(uint8_t *buf, uint8_t len) {
  uint16_t crc = 0xFFFF;
  for (uint8_t i = 0; i < len; i++) {
    crc ^= buf[i];
    for (uint8_t j = 0; j < 8; j++)
      crc = (crc & 1) ? (crc >> 1) ^ 0xA001 : crc >> 1;
  }
  return crc;
}

void sendRawModbusCoilWrite(uint8_t slaveAddr, CoilAddress coilAddr, bool on) {
  uint8_t packet[8] = {
    slaveAddr, 0x05,
    coilAddr >> 8, coilAddr & 0xFF,
    on ? 0xFF : 0x00, 0x00,
    0, 0
  };
  uint16_t crc = ModbusCRC(packet, 6);
  packet[6] = crc & 0xFF;
  packet[7] = crc >> 8;

  Serial.println("🔁 Gửi lệnh Modbus thủ công:");
  for (uint8_t i = 0; i < 8; i++) Serial.printf("%02X ", packet[i]);
  Serial.println();

  digitalWrite(MAX485_DE_RE, HIGH);
  delay(2);
  Serial2.write(packet, 8);
  Serial2.flush();
  delay(2);
  digitalWrite(MAX485_DE_RE, LOW);
}

bool readWithRetry(ModbusMaster &node, uint16_t addr, uint16_t count, bool input = false, uint8_t retries = 3) {
  for (uint8_t i = 0; i < retries; i++) {
    auto res = input ? node.readInputRegisters(addr, count) : node.readHoldingRegisters(addr, count);
    if (res == node.ku8MBSuccess) return true;
    delay(50);
  }
  return false;
}

bool readCurrentSelec(ModbusMaster &node, float &ia, float &ib, float &ic) {
  if (!readWithRetry(node, 16, 6, true)) return false;
  ia = toFloat(node.getResponseBuffer(0), node.getResponseBuffer(1));
  ib = toFloat(node.getResponseBuffer(2), node.getResponseBuffer(3));
  ic = toFloat(node.getResponseBuffer(4), node.getResponseBuffer(5));
  return true;
}

bool addSelecData(ModbusMaster &node, const char *label, JsonObject &obj) {
  if (!readWithRetry(node, 0, 64, true)) {
    unsigned long now = millis();
    if (strcmp(label, "selec1") == 0 && now - lastErrorSelec1 > errorPrintInterval) {
      Serial.println("FAIL selec1 read failed");
      lastErrorSelec1 = now;
    } else if (strcmp(label, "selec2") == 0 && now - lastErrorSelec2 > errorPrintInterval) {
      Serial.println("FAIL selec2 read failed");
      lastErrorSelec2 = now;
    }
    return false;
  }
  JsonArray regs = obj.createNestedArray("regs");
  for (uint8_t i = 0; i < 64; i++) regs.add(node.getResponseBuffer(i));
  return true;
}

bool pulseCoil(ModbusMaster *node, CoilAddress addr, unsigned long delayTime = 300) {
  if (node->writeSingleCoil(addr, 0xFF00) != node->ku8MBSuccess) return false;
  delay(delayTime);
  return node->writeSingleCoil(addr, 0x0000) == node->ku8MBSuccess;
}

void mqttCallback(char *topic, byte *payload, unsigned int length) {
  Serial.printf("[MQTT] MQTT topic: %s\n", topic);

  StaticJsonDocument<100> doc;
  if (deserializeJson(doc, payload, length)) return;

  int id = doc["generatorId"];
  String action = doc["action"];
  ModbusMaster *node = (id == 1) ? &ats1 : &ats2;

  if (action == "start") {
    sendRawModbusCoilWrite(id, COIL_START, true);
    delay(1000); return;
  }
  if (action == "stop") {
    sendRawModbusCoilWrite(id, COIL_STOP, true);
    delay(1000); return;
  }
  if (action == "auto_on") {
    sendRawModbusCoilWrite(id, COIL_AUTO_MANUAL, true);
    delay(1000); return;
  }
  if (action == "auto_off") {
    bool success = node->writeSingleCoil(COIL_AUTO_MANUAL, 0x0000) == node->ku8MBSuccess;
    Serial.println(success ? "[CMD] MANUAL" : "FAIL Lỗi MANUAL");
    return;
  }

  CoilAddress addr;
  if (action == "close_acb") addr = COIL_CLOSE_ACB;
  else if (action == "open_acb") addr = COIL_OPEN_ACB;
  else if (action == "reset_alarm") addr = COIL_ALARM_RESET;
  else { Serial.println("FAIL Lệnh không hợp lệ"); return; }

  bool ok = pulseCoil(node, addr, 1000);
  Serial.printf("[CMD] %s ATS %d %s\n", action.c_str(), id, ok ? "OK" : "FAIL");
}

void reconnectMQTT() {
  while (!mqttClient.connected()) {
    Serial.print("MQTT...");
    if (mqttClient.connect("ESP32Client")) {
      Serial.println("OK");
      mqttClient.subscribe("ats/control");
    } else {
      Serial.println("FAIL");
      delay(2000);
    }
  }
}

void setupModbus() {
  Serial2.begin(9600, SERIAL_8N1, RXD2, TXD2);
  ModbusMaster *nodes[] = { &ats1, &ats2, &selec1, &selec2 };
  uint8_t ids[] = { 1, 2, 3, 4 };
  for (int i = 0; i < 4; i++) {
    nodes[i]->begin(ids[i], Serial2);
    nodes[i]->preTransmission(preTransmission);
    nodes[i]->postTransmission(postTransmission);
  }
}

bool addATSData(ModbusMaster &node, const char *label, float ia, float ib, float ic, JsonObject &gen) {
  if (!readWithRetry(node, 1000, 20)) {
    unsigned long now = millis();
    if (strcmp(label, "gen1") == 0 && now - lastErrorGen1 > errorPrintInterval) {
      Serial.println("FAIL gen1 read failed");
      lastErrorGen1 = now;
    } else if (strcmp(label, "gen2") == 0 && now - lastErrorGen2 > errorPrintInterval) {
      Serial.println("FAIL gen2 read failed");
      lastErrorGen2 = now;
    }
    return false;
  }
  lastSuccessRead = millis();
  for (int i = 0; i < 20; i++) gen[String("r") + i] = node.getResponseBuffer(i);
  gen["freq1"] = node.getResponseBuffer(9) * 10 / 100.0;
  gen["freq2"] = node.getResponseBuffer(19) * 10 / 100.0;

  if (readWithRetry(node, 0, 1)) gen["auto_mode"] = (node.getResponseBuffer(0) & (1 << 8)) > 0;
  else gen["auto_mode"] = -1;

  gen["ia"] = ia;
  gen["ib"] = ib;
  gen["ic"] = ic;
  return true;
}

void setupWebServer() {
  server.on("/", HTTP_GET, []() {
    server.send(200, "text/html",
      "<form method='POST' action='/update' enctype='multipart/form-data'>"
      "<input type='file' name='update'><br><br>"
      "<input type='submit' value='Upload Firmware'>"
      "</form>");
  });

  server.on("/update", HTTP_POST, []() {
    server.send(200, "text/plain", (Update.hasError()) ? "FAIL" : "OK. Restarting...");
    delay(1000);
    ESP.restart();
  }, []() {
    HTTPUpload& upload = server.upload();
    if (upload.status == UPLOAD_FILE_START) {
      Serial.printf("⏫ Bắt đầu OTA: %s\n", upload.filename.c_str());
      if (!Update.begin()) Update.printError(Serial);
    } else if (upload.status == UPLOAD_FILE_WRITE) {
      if (Update.write(upload.buf, upload.currentSize) != upload.currentSize)
        Update.printError(Serial);
    } else if (upload.status == UPLOAD_FILE_END) {
      if (Update.end(true)) Serial.printf("✅ OTA thành công: %u bytes\n", upload.totalSize);
      else Update.printError(Serial);
    }
  });

  server.begin();
  Serial.println("🌐 Web OTA sẵn sàng tại: http://<IP>");
}

void setup() {
  Serial.begin(115200);
  pinMode(MAX485_DE_RE, OUTPUT);
  digitalWrite(MAX485_DE_RE, LOW);

  Ethernet.init(4);
  Ethernet.begin(mac);
  mqttClient.setServer(mqttServer, 1883);
  mqttClient.setCallback(mqttCallback);
  setupModbus();

  Serial.print("ESP32 IP: ");
  Serial.println(Ethernet.localIP());

  setupWebServer();
  lastSuccessRead = millis();
}

void loop() {
  server.handleClient();

  if (!mqttClient.connected()) reconnectMQTT();
  mqttClient.loop();

  if (millis() - lastSuccessRead > MAX_TIMEOUT) {
    Serial.println("TIMEOUT - Restarting...");
    delay(1000);
    ESP.restart();
  }

  if (millis() - lastPoll >= POLL_INTERVAL) {
    lastPoll = millis();
    float ia1 = -1, ib1 = -1, ic1 = -1, ia2 = -1, ib2 = -1, ic2 = -1;
    readCurrentSelec(selec1, ia1, ib1, ic1);
    readCurrentSelec(selec2, ia2, ib2, ic2);

    StaticJsonDocument<2048> doc;
    JsonObject gen1Obj = doc.createNestedObject("gen1");
    bool ok1 = addATSData(ats1, "gen1", ia1, ib1, ic1, gen1Obj);
    JsonObject gen2Obj = doc.createNestedObject("gen2");
    bool ok2 = addATSData(ats2, "gen2", ia2, ib2, ic2, gen2Obj);
    JsonObject selec1Obj = doc.createNestedObject("selec1");
    bool ok3 = addSelecData(selec1, "selec1", selec1Obj);
    JsonObject selec2Obj = doc.createNestedObject("selec2");
    bool ok4 = addSelecData(selec2, "selec2", selec2Obj);

    if (ok1 || ok2 || ok3 || ok4) {
      String payload;
      serializeJson(doc, payload);
      mqttClient.publish("ats/data", payload.c_str());
      Serial.println("[SEND] MQTT payload:");
      Serial.println(payload);
    }
  }
}

// NexaSense - prototipo educacional com falhas intencionais.
// Executar apenas no laboratorio Wokwi. Nenhuma credencial real e usada.
#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>
#include <DHT.h>

const int SENSOR_PIN = 15;
const int ALERT_PIN = 2;
const char *DEVICE_ID = "nexasense-lab-01";
const char *FIRMWARE_VERSION = "1.0.0-lab";
const char *INTERNAL_CONFIG = "LAB_ONLY_CONFIG_nao_e_segredo_real";
const char *WIFI_SSID = "Wokwi-GUEST";

DHT sensor(SENSOR_PIN, DHT22);
WebServer server(80); // HTTP simples, sem TLS: objeto da avaliacao.
float temperature = NAN;
float humidity = NAN;
float alertThreshold = 30.0;
unsigned long lastReading = 0;
String serialCommand;

String telemetry() {
  if (isnan(temperature) || isnan(humidity)) return "{\"error\":\"sensor_not_ready\"}";
  return String("{\"device\":\"") + DEVICE_ID + "\",\"temperature\":" +
         String(temperature, 1) + ",\"humidity\":" + String(humidity, 1) +
         ",\"threshold\":" + String(alertThreshold, 1) +
         ",\"alert\":" + (temperature >= alertThreshold ? "true" : "false") + "}";
}

String debugInfo() {
  // Falha intencional: configuracao interna exposta em UART e HTTP.
  return String("device=") + DEVICE_ID + "\nfirmware=" + FIRMWARE_VERSION +
         "\ninternal_config=" + INTERNAL_CONFIG +
         "\ntransport=HTTP sem TLS\nupdate=USB UART por recompilacao; sem OTA\n";
}

void setup() {
  Serial.begin(115200);
  pinMode(ALERT_PIN, OUTPUT);
  sensor.begin();
  Serial.println("\n=== NexaSense laboratorio autorizado ===");
  Serial.print(debugInfo());
  Serial.println("UART: digite INFO para repetir o diagnostico.");

  // A rede virtual permite acessar apenas o servidor deste projeto.
  // O firmware nao faz requisicoes para servicos externos.
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, "", 6);
  unsigned long start = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - start < 15000) delay(100);
  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("WiFi conectado. IP virtual: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("WiFi indisponivel. UART e sensor continuam funcionando.");
  }

  server.on("/", HTTP_GET, []() {
    server.send(200, "text/plain", "NexaSense LAB: /telemetry /debug /config?threshold=30");
  });
  server.on("/telemetry", HTTP_GET, []() {
    server.send(isnan(temperature) ? 503 : 200, "application/json", telemetry());
  });
  server.on("/debug", HTTP_GET, []() {
    server.send(200, "text/plain", debugInfo());
  });
  server.on("/config", HTTP_GET, []() {
    // Falha intencional: alteracao de estado por GET, sem autenticacao.
    if (!server.hasArg("threshold")) {
      server.send(400, "text/plain", "Use threshold entre 0 e 80");
      return;
    }
    String argument = server.arg("threshold");
    char *end = nullptr;
    float value = strtof(argument.c_str(), &end);
    if (end == argument.c_str() || *end != '\0' || !isfinite(value) || value < 0 || value > 80) {
      server.send(400, "text/plain", "Valor invalido");
      return;
    }
    alertThreshold = value;
    digitalWrite(ALERT_PIN, !isnan(temperature) && temperature >= alertThreshold);
    Serial.printf("CONFIG sem autenticacao: threshold=%.1f\n", alertThreshold);
    server.send(200, "application/json", telemetry());
  });
  server.onNotFound([]() { server.send(404, "text/plain", "Rota inexistente"); });
  server.begin();
  Serial.println("HTTP pronto. Acesso local: http://localhost:8180/telemetry");
}

void loop() {
  server.handleClient();
  if (millis() - lastReading >= 2500) {
    lastReading = millis();
    temperature = sensor.readTemperature();
    humidity = sensor.readHumidity();
    digitalWrite(ALERT_PIN, !isnan(temperature) && temperature >= alertThreshold);
    Serial.println(telemetry());
  }
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') {
      serialCommand.trim();
      if (serialCommand == "INFO") Serial.print(debugInfo());
      else Serial.println("Comando disponivel: INFO");
      serialCommand = "";
    } else if (serialCommand.length() < 40) serialCommand += c;
  }
  delay(2);
}

#include <Bounce.h>

constexpr int RECORD_PIN = 2;
constexpr int PLAY_PIN   = 4;
constexpr int STOP_PIN   = 6;
constexpr int DEBOUNCE_MS = 20;

Bounce recordButton(RECORD_PIN, DEBOUNCE_MS);
Bounce playButton(PLAY_PIN, DEBOUNCE_MS);
Bounce stopButton(STOP_PIN, DEBOUNCE_MS);

void setup() {
  pinMode(RECORD_PIN, INPUT_PULLUP);
  pinMode(PLAY_PIN, INPUT_PULLUP);
  pinMode(STOP_PIN, INPUT_PULLUP);

  Serial.begin(115200);
}

void loop() {
  recordButton.update();
  playButton.update();
  stopButton.update();

  if (recordButton.fallingEdge()) {
    Serial.println("RECORD_START");
  }

  if (recordButton.risingEdge()) {
    Serial.println("RECORD_END");
  }

  if (playButton.fallingEdge()) {
    Serial.println("PLAY");
  }

  if (stopButton.fallingEdge()) {
    Serial.println("STOP");
  }
}
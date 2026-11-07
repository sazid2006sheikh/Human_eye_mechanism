#include <Servo.h>

Servo horizontal;
Servo vertical;

void setup() {
  Serial.begin(9600);

  horizontal.attach(9);
  vertical.attach(10);

  horizontal.write(90);
  vertical.write(90);
}

void loop() {
  if (Serial.available()) {
    int x = Serial.parseInt();
    int y = Serial.parseInt();

    if (Serial.read() == '\n') {
      horizontal.write(constrain(x, 0, 180));
      vertical.write(constrain(y, 0, 180));
    }
  }
}
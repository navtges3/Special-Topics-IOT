#define BUTTON  4
#define LED     5

int buttonLastState = LOW;

void setup() {
  // put your setup code here, to run once:
  pinMode(LED, OUTPUT);
  pinMode(BUTTON, INPUT);
 }

void loop() {
  // put your main code here, to run repeatedly:
  int val = digitalRead(BUTTON);

  if(val == LOW && buttonLastState == HIGH) {
    digitalWrite(LED, HIGH);
    delay(1000);
    digitalWrite(LED, LOW);
  }
  buttonLastState = val;
}

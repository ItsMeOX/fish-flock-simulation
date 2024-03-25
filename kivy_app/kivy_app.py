from kivy.app import App
from kivy.uix.label import Label
from kivy.clock import Clock
from plyer import accelerometer

class AccelerometerApp(App):
    def build(self):
        self.label = Label(text="Acceleration: ")
        Clock.schedule_interval(self.update_acceleration, 1.0 / 30.0)  # Update every 1/30th of a second
        accelerometer.enable()  # Enable accelerometer
        return self.label

    def update_acceleration(self, dt):
        acceleration = accelerometer.acceleration  # Get accelerometer data
        if acceleration:
            self.label.text = "Acceleration: {:.2f}, {:.2f}, {:.2f}".format(*acceleration)


if __name__ == '__main__':
    AccelerometerApp().run()
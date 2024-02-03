import sys
import serial
from PyQt5 import QtWidgets, QtCore
import RPi.GPIO as GPIO
import time
import threading

font = QFont()
font.setPointSize(12)


# Relais Alim Arduino
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)

def relay_on(): # Function to turn the relay ON
    GPIO.output(17, GPIO.HIGH) 
    
def relay_off():# Function to turn the relay OFF
    GPIO.output(17, GPIO.LOW) 

# App
class SerialApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.isRunning = False

        # Initialize the serial connection
        self.arduinoSerial = serial.Serial()
        self.arduinoSerial.baudrate = 115200 # need to mach the Arduino code
        self.arduinoSerial.timeout = 1
        self.arduinoSerial.port = '/dev/ttyS0'  # Replace with the correct port

        # Attempt to open the serial port
        try:
            self.arduinoSerial.open()
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}")

        # Create main widget and layout
        mainWidget = QtWidgets.QWidget()
        self.setCentralWidget(mainWidget)
        mainLayout = QtWidgets.QHBoxLayout(mainWidget)

        # Create splitter
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)

        # Left Panel for Sliders and Buttons
        leftPanel = QtWidgets.QWidget()
        leftLayout = QtWidgets.QVBoxLayout(leftPanel)

        # Add "Settings" label at the top of the left panel
        leftPanelLabel = QtWidgets.QLabel("Settings")
        leftPanelLabel.setAlignment(QtCore.Qt.AlignCenter)
        leftLayout.addWidget(leftPanelLabel)

        self.createSliderLayout(leftLayout, "IPI", 0, 200, 40)
        self.createSliderLayout(leftLayout, "Nrep", 0, 150, 90)
        self.createSliderLayout(leftLayout, "ITI", 0, 60, 10)

        # Add a label for "Trigger buttons:"
        triggerButtonsLabel = QtWidgets.QLabel("Trigger buttons:")
        leftLayout.addWidget(triggerButtonsLabel)

        # Create a horizontal layout for buttons
        buttonsLayout = QtWidgets.QHBoxLayout()

        # Create buttons and add them to the buttons layout
        self.cs_button = QtWidgets.QPushButton('Cs')
        self.cs_button.setFixedHeight(80) 
        self.cs_button.setFont(font)
        self.cs_button.clicked.connect(self.CsButtonPushed)
        buttonsLayout.addWidget(self.cs_button)
        
        self.ts_button = QtWidgets.QPushButton('Ts')
        self.ts_button.setFixedHeight(80)
        self.ts_button.setFont(font)

 
        self.ts_button.clicked.connect(self.TsButtonPushed)
        buttonsLayout.addWidget(self.ts_button)

        self.ttl_button = QtWidgets.QPushButton('Bio')
        self.ttl_button.setFixedHeight(80) 
        self.ttl_button.setFont(font)
        self.ttl_button.clicked.connect(self.TTLButtonPushed)
        buttonsLayout.addWidget(self.ttl_button)

        # Add buttons layout to the left panel layout
        leftLayout.addLayout(buttonsLayout)

        # Create a label for displaying messages
        self.triggercatch = QtWidgets.QLabel()
        leftLayout.addWidget(self.triggercatch)

        # Add left panel to splitter
        splitter.addWidget(leftPanel)

        # Right Panel for future content
        rightPanel = QtWidgets.QWidget()
        rightLayout = QtWidgets.QVBoxLayout(rightPanel)

        # Add "ppTMS GUI" label at the top of the right panel
        rightPanelLabel = QtWidgets.QLabel("ppTMS GUI")
        rightPanelLabel.setAlignment(QtCore.Qt.AlignCenter)
        rightLayout.addWidget(rightPanelLabel)

        # Create a progress bar under the Start button
        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setFixedHeight(50)  
        rightLayout.addWidget(self.progressBar)

        # Create Start, Pause, Stop buttons in the right panel
        self.startButton = QtWidgets.QPushButton('Start')
        self.startButton.setFixedHeight(80) 
        self.startButton.clicked.connect(self.startButtonPushed)
        rightLayout.addWidget(self.startButton)
        
        self.pauseButton = QtWidgets.QPushButton('Pause')
        self.pauseButton.setFixedHeight(80)  
        rightLayout.addWidget(self.pauseButton)

        self.stopButton = QtWidgets.QPushButton('Stop')
        self.stopButton.setFixedHeight(80)  
        self.stopButton.clicked.connect(self.stopButtonPushed)
        rightLayout.addWidget(self.stopButton)
        
        # Spacer at the bottom (expanding spacer)
        bottomSpacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        rightLayout.addItem(bottomSpacer)

        # Add right panel to splitter
        splitter.addWidget(rightPanel)

        # Add splitter to main layout
        mainLayout.addWidget(splitter)

        # Set the size of the window
        self.setGeometry(100, 100, 800, 400)
        self.setWindowTitle('Serial Communication App')
        
        self.loopPaused = threading.Event()
        self.loopPaused.set()  # Initially set to True to allow loop execution
        self.loopCondition = threading.Condition()
        self.pauseButton.clicked.connect(self.pauseButtonPushed)

        
    def adjustSplitter(self):
      window_width = self.width()
      self.splitter.setSizes([window_width // 2, window_width // 2])

    def createSliderLayout(self, parentLayout, sliderName, minValue, maxValue, defaultValue):
        sliderLayout = QtWidgets.QHBoxLayout()

        sliderNameLabel = QtWidgets.QLabel(sliderName)
        sliderLayout.addWidget(sliderNameLabel)

        slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        slider.setRange(minValue, maxValue)
        slider.setValue(defaultValue)
        slider.valueChanged.connect(lambda value, name=sliderName: self.sliderValueChanged(value, name))
        sliderLayout.addWidget(slider)

        valueLabel = QtWidgets.QLabel(str(defaultValue))
        sliderLayout.addWidget(valueLabel)

        parentLayout.addLayout(sliderLayout)

        setattr(self, f"{sliderName.lower()}Slider", slider)
        setattr(self, f"{sliderName.lower()}ValueLabel", valueLabel)

    def sliderValueChanged(self, value, name):
        label = getattr(self, f"{name.lower()}ValueLabel")
        label.setText(str(value))

    def TsButtonPushed(self):
        try:
            self.arduinoSerial.write(b'SET,test,1')
            self.triggercatch.setText('Ts pressed')
        except Exception as e:
            self.triggercatch.setText('!!! Serial is not connected !!!')

    def CsButtonPushed(self):
        try:
            self.arduinoSerial.write(b'SET,test,2')
            self.triggercatch.setText('Cs pressed')
        except Exception as e:
            self.triggercatch.setText('!!! Serial is not connected !!!')

    def TTLButtonPushed(self):
        try:
            self.arduinoSerial.write(b'SET,test,3')
            self.triggercatch.setText('Bio pressed')
        except Exception as e:
            self.triggercatch.setText('!!! Serial is not connected !!!')
            
    def startButtonPushed(self):
        ipi = self.ipiSlider.value()
        if not self.isRunning:
            self.isRunning = True
            self.startButton.setText("Started")
           
            
            # Send the IPI command
            self.arduinoSerial.write(f'SET,IPI1,{ipi}'.encode())
            # Start the stimulation loop in a separate thread
            self.thread = threading.Thread(target=self.runStimulationLoop)
            self.thread.start()

    def runStimulationLoop(self):
        numLoops = self.nrepSlider.value()
        iti = self.itiSlider.value()
    
        for i in range(numLoops):
    
            with self.loopCondition:
                while not self.loopPaused.is_set():
                    self.loopCondition.wait()  # Wait if paused
                if not self.isRunning:
                    break  # Break the loop if stop button was pressed
                start_time = time.time()
                self.arduinoSerial.write(b'1')
                # Update UI
                self.updateProgressBar(i, numLoops)
                # Calculate the remaining time to sleep
                elapsed_time = time.time() - start_time
                remaining_time = max(0, iti - elapsed_time)
                time.sleep(remaining_time)
    
        self.progressBar.setValue(100) if self.isRunning else self.progressBar.setValue(0)
        self.isRunning = False
        self.startButton.setText("Start")
        
    def updateProgressBar(self, i, numLoops):
        # Update the progress bar in the main thread
        progress = int((i / numLoops) * 100)
        self.progressBar.setValue(progress)
        
    def pauseLoop(self):
        self.loopPaused.clear()  # Clear the event to pause the loop

    def resumeLoop(self):
        with self.loopCondition:
            self.loopPaused.set()  # Set the event to resume the loop
            self.loopCondition.notify()  # Notify the loop to continue

    def pauseButtonPushed(self):
        if self.isRunning and self.loopPaused.is_set():
            self.pauseLoop()
            self.pauseButton.setText("Resume")
        else:
            self.resumeLoop()
            self.pauseButton.setText("Pause")

    def stopButtonPushed(self):
        self.isRunning = False
        self.startButton.setText("Start")
        self.progressBar.setValue(0)
        with self.loopCondition:
            self.loopPaused.set()  # Make sure the loop resumes if it was paused
            self.loopCondition.notify()


    def closeEvent(self, event):
        relay_off()  # Turn off the relay when the application is closed
        if self.arduinoSerial.is_open:
            self.arduinoSerial.close()  # Close the serial port if it's open
        GPIO.cleanup()  # Clean up GPIO
        super().closeEvent(event)

if __name__ == '__main__':
    relay_on()  # Turn on the relay at the start of the application
    app = QtWidgets.QApplication(sys.argv)
    mainWin = SerialApp()
    mainWin.show()
    sys.exit(app.exec_())


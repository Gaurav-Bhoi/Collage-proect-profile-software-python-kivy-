from kivy.resources import resource_add_path, resource_find
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty, StringProperty
import pyrebase
from kivy import utils
import face_recognition
import cv2
import numpy as np
import sys, os

firebaseConf = {
        '''Enter your firebase database credentials here'''
    }
firebase = pyrebase.initialize_app(firebaseConf)
database = firebase.database()

face_data = database.child('Face Encoding').get().val()
face_data = dict(face_data)
keyDict = list(face_data.keys())
valueDict = []
for items in list(face_data.values()):
    valueDict.append(list(items.values())[0])

whole_data = database.child('Employee').get().val()



class Box(BoxLayout):
    def password_authentication(self, emp_id_txtip, emp_id_password):
        password = database.child('Employee').child(emp_id_txtip).child('password').get().val()

        try:
            if emp_id_password == password:
                global Id
                Id = emp_id_txtip
                self.ids.screen_manager.current = 'profile_screen'

            else:
                self.ids.login_screen.ids.emp_id_txtip.text = ''
                self.ids.login_screen.ids.emp_id_password.text = ''
        except:
            self.ids.login_screen.ids.emp_id_txtip.text = ''
            self.ids.login_screen.ids.emp_id_password.text = ''

    def face_authentication(self):
        video_capture = cv2.VideoCapture(0)

        while True:
            _, frame = video_capture.read()

            currentFaceLocation = face_recognition.face_locations(frame)
            currentFaceEncoding = face_recognition.face_encodings(frame, currentFaceLocation)

            for faceEncoding in currentFaceEncoding:
                matches = face_recognition.compare_faces(valueDict, faceEncoding)
                face_distances = face_recognition.face_distance(valueDict, faceEncoding)
                best_match_index = np.argmin(face_distances)

                if matches[best_match_index]:
                    id = keyDict[best_match_index]
                    global Id
                    Id = id
                    self.ids.screen_manager.current = 'profile_screen'
                break
            break

    def selected(self, image):
        self.ids.profile_screen.ids.img.background_normal = image[0]

class Profile_Button(BoxLayout, Button):
    label_1 = StringProperty()
    label_2 = StringProperty()
    id = StringProperty()

class LogIn_Screen(Screen):
    pass

class ProfileScreen(Screen):
    def on_pre_enter(self, *args):
        self.ids.employee_id_label.text = Id
        self.ids.employee_name_label.text = database.child('Employee').child(Id).child('name').get().val()
        self.ids.employee_designation_label.text = database.child('Employee').child(Id).child('designation').get().val()
        self.ids.employee_email_label.text = database.child('Employee').child(Id).child('email').get().val()

    def open_fileChooser_popup(self):
        FileChooserPopup().open()

class ChatScreen(Screen):
    def on_pre_enter(self, *args):
        for key, value in whole_data.items():
            if key != str(Id):
                button = Profile_Button(label_1=('Id - ' + key), label_2=('Name - ' + value.get('name')), id=str(key))
                self.ids.employee_chats.add_widget(button)
                button.bind(on_release=self.callback)

    def on_leave(self, *args):
        self.ids.employee_chats.clear_widgets()

    def callback(self, instance):
        global sending_address
        sending_address = instance.id
        self.parent.current = 'chatting_screen'
        self.parent.transition.direction = 'left'

class ChattingScreen(Screen):
    def on_pre_enter(self, *args):
        self.ids.emp_name.text = database.child('Employee').child(sending_address).get().val().get('name')
        self.ids.emp_id.text = sending_address
        Clock.schedule_interval(self.receive_messages, 0.1)

    def on_leave(self, *args):
        Clock.unschedule(self.receive_messages)

    def send_message(self, message):
        if message != '':
            msg = Label(text=message, font_size=17, text_size=self.size,
                        halign='right', valign='middle', padding=(20, 0),
                        height=30, size_hint_y=None, color=utils.get_color_from_hex('#FF356C'))
            self.ids.messages.add_widget(msg)
            database.child('Employee').child(sending_address).child('Message').set({Id: message})

    def receive_messages(self, dt):
        try:
            emp_id = self.ids.emp_id.text
            message = database.child('Employee').child(Id).child('Message').get().val().get(emp_id)
            msg = Label(text=message, font_size=17, text_size=self.size, halign='left', valign='middle',padding=(20, 0), height=30, size_hint_y=None, color=(0, 0, 0, 1))
            self.ids.messages.add_widget(msg)
            database.child('Employee').child(Id).child('Message').child(emp_id).remove()
        except:
            pass

class VideoMeet(Screen):
    pass

class FileChooserPopup(Popup):
    pass


Window.size = (400,750)
class MainApp(App):
    login_screen = LogIn_Screen()
    profile_screen = ProfileScreen()

    def build(self):
        return Box()

if __name__ == '__main__':
    if hasattr(sys, '_MEIPASS'):
        resource_add_path(os.path.join(sys._MEIPASS))
    MainApp().run()
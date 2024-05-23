# Program name: StoryApp.py
#
# Description: A flask web application for story writer
#
# References:
#  1. Flask – (Creating first simple application)
#      https://www.geeksforgeeks.org/flask-creating-first-simple-application/
#  2. Story Generator App Using Python
#      https://www.geeksforgeeks.org/story-generator-app-using-python/
#  3. How to build a Random Story Generator using Python?
#      https://www.geeksforgeeks.org/how-to-build-a-random-story-generator-using-python/
#  4. HTML Form Elements
#     https://www.w3schools.com/html/html_form_elements.asp
#  5. Python Text To Speech | pyttsx module
#      https://www.geeksforgeeks.org/python-text-to-speech-pyttsx-module/?ref=lbp
#  6. Build a Text to Speech Service with Python Flask Framework
#      https://dev.to/siddheshshankar/build-a-text-to-speech-service-with-python-flask-framework-3966
#  7. Flask - Calling python function on button OnClick event
#      https://stackoverflow.com/questions/42601478/flask-calling-python-function-on-button-onclick-event
#  8. 10 Lines Short Stories With Moral Lessons for Kids
#      https://ofhsoupkitchen.org/short-stories-with-morals#:~:text=The%20Dog%20and%20the%20Bone,a%20bone%20in%20its%20mouth.
#  9. CSS Links
#      https://www.w3schools.com/css/css_link.asp
# 10. CSS Text Shadow
#      https://www.w3schools.com/css/css_text_shadow.asp
#
# -------------------------------------------------------------------------------------------------------------------------
# Program Listing:
#   1. StoryApp.py (merge with app.py program)
#   2. templates/archive.html - ok
#   3. templates/forgetpass.html
#   4. templates/home.html
#   5. templates/index.html - ok
#   6. templates/login.html
#   7. templates/nav.html --> templates/base.html - not yet
#   8. templates/signup.html
#   9. templates/story.html - ok2which python
#  10. templates/storylist.html - ok2
#  11. static/login.css
#  12. static/nav.css --> static/base.css - not yet
#  13. static/signup.css
#  14. static/styles.css --> static/base.css - not yet
#  15. static/images/bookworm.gif - ok2
#  16. static/images/dustbin.jpg - ok2
#  17. static/images/text-to-speech.jpg - ok2
#  18. static/images/writing.gif - ok2
#  19. static/images/trash-can.gif - ok2
#  20. static/images/storytime.gif - ok2
#  21. static/login_img.jpg (suggest to move to static\images folder)
#  22. stories.csv (create automatically by StoryApp.py)
#  
# -------------------------------------------------------------------------------------------------------------------------


from StoryApp import app

if __name__ == '__main__':
    app.run(debug=True)

import pyttsx3

engine = pyttsx3.init()
voices = engine.getProperty('voices')
print("Available voices:")
for i, v in enumerate(voices):
    print(f'{i}: {v.name}')

print('---')
print('Initial voice:', engine.getProperty('voice'))

# Try setting to voice index 1 (Zira)
engine.setProperty('voice', voices[1].id)
print('Set voice to voices[1].id')
print('Voice after setting:', engine.getProperty('voice'))

engine.setProperty('rate', 170)

print("Speaking with current voice (should be Zira):")
engine.say('Hello, I am Tommy with a female voice.')
engine.runAndWait()

# Now try with David
engine.setProperty('voice', voices[0].id)
print("Speaking with David voice:")
engine.say('Now I am speaking with the male voice.')
engine.runAndWait()

# Back to Zira
engine.setProperty('voice', voices[1].id)
print("Speaking with Zira again:")
engine.say('Back to female voice.')
engine.runAndWait()
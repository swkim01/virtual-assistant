import aiml

kernel = aiml.Kernel()
kernel.learn("std-startup.xml")

kernel.respond("load aiml b")

# Press CTRL-C to break this loop
while True:
    print kernel.respond(raw_input("Input >> "))


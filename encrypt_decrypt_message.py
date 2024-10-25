
import random
import string

def random_chars():
    return "".join(random.choices(string.ascii_letters + string.digits, k=3))

enter_message = input("Input your message: ")

split_word = enter_message.split(" ")

option = input("Enter 1 for encrypting 2 for decrypting: ")

decode = []
if option == "1":
    coding = True
else:
    coding = False

if coding:
    for word in split_word:
        if len(word) >= 3:
            c = random_chars()
            f = random_chars()
            encrypt_word = c + word[1:] + word[0] + f
            decode.append(encrypt_word)
        else:
            decode.append(word[::-1])
else:
    for word in split_word:
        if len(word) >= 9:
            chars_removal = word[3:-3]
            chars_removal = chars_removal[-1] + chars_removal[:-1]
            decode.append(chars_removal)
        else:
            decode.append(word[::-1])

print(" ".join(decode))

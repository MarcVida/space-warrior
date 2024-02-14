myd = {
    1.9: "ye",
    1.633: "hello",
    4.2: "world"
}

res = sorted(myd.items(), key = lambda x: x[0])

print(res)
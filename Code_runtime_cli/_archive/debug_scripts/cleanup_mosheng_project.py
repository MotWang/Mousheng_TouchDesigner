old = op("/project1")
if old is not None:
    old.destroy()
    print("Removed old /project1 sample network.")
else:
    print("No /project1 sample network found.")

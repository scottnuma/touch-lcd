from subprocess import check_output

if __name__ == "__main__":
    cmd = input(" > ")
    while cmd:
        print(check_output(cmd, shell=True).decode("utf-8"))
        cmd = input(" > ")
    print("Exiting...")

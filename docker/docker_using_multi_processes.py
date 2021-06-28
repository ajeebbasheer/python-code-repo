import subprocess
import shlex
import os
from concurrent.futures import ProcessPoolExecutor

def spawnTests(s):
    i = 0
    while True:
        try:
            subprocess.call(s, shell=True)
            break
        except Exception as e:
            print('ERROR: Could not launch tests - {e}'.format(e=e))
            traceback.print_exc()
            i+=1
            if i==10 : break
            time.sleep(1)

def execute_command(sp_command, cwd=None):
    try:
        sp_out, sp_err = None, None
        process = subprocess.Popen(shlex.split(sp_command),
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        cwd=cwd)

        sp_out, sp_err = process.communicate()

        if process.returncode == 124 and not sp_err:
            sp_err = "Timeout"

    except Exception as excp:
        print(f"Exception in running sub process commands:{excp}")
        return sp_out, sp_err

    return sp_out, sp_err

def get_tests():
    tests = []
    with open("failed_tests.txt", "r") as file:
        while file.tell() != os.fstat(file.fileno()).st_size:
            line = file.readline()
            tests.append(f"/etc/certification1/{line[:-1]}")

    return tests[:-1]

def docker_run(test):
    name = os.getpid()
    res = "/opt/results"
    execute_command(f"mkdir -p {res}")
    file_name = test.split('/')[-1][:-5]
    cmd = f"docker run --rm -ti psb_worker_image:0.30 rally task start {test} > {res}/{file_name}.out 2> {res}/{file_name}.info"
    # cmd = "ls"
    # os.spawnl(os.P_NOWAIT, cmd)
    print(f"Process-{name} started running {file_name}..")
    spawnTests(cmd)

def run_tests():
    tests = get_tests()
    # tests=["/etc/certification1/cinder/17-create-volume-type-and-encryption-type/17-1-create-volume-type-and-encryption-type.yaml", "/etc/certification1/nova2/38-boot-and-live-migrate-server/38-1a-boot-and-live-migrate-server.yaml"]
    # docker_run(test)

    with ProcessPoolExecutor(max_workers = 5) as pool:
        for test in tests:
            pool.submit(docker_run, test)


if __name__ == "__main__":
    # print(f"get_tests: {get_tests()}")
    run_tests()


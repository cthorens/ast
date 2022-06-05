from pandare import Panda

panda = Panda(generic="x86_64")

recording_name = "test_recording"

@panda.queue_blocking
def run_cmd():
    panda.record_cmd(
            "./rust-readelf/target/x86_64-unknown-linux-gnu/debug/rust-readelf -f ls -h",
            recording_name=recording_name,
            copy_directory="app",
            setup_command="cd /root/app",
            )

    panda.end_analysis()

panda.run()

panda.set_pandalog("pandalog.plog")


panda.load_plugin("file_taint", {"filename":"/root/app/ls","pos":True})
panda.load_plugin("tainted_instr",{"summary":False})
panda.load_plugin("tainted_branch",{"summary":False})
panda.load_plugin("loaded_libs")

panda.run_replay(recording_name)

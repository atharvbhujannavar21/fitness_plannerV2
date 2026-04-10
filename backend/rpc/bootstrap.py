from pathlib import Path

from grpc_tools import protoc


def ensure_generated() -> None:
    proto_dir = Path(__file__).resolve().parent.parent / "grpc"
    proto_file = proto_dir / "fitness.proto"
    pb2_file = proto_dir / "fitness_pb2.py"
    grpc_file = proto_dir / "fitness_pb2_grpc.py"

    if (
        pb2_file.exists()
        and grpc_file.exists()
        and pb2_file.stat().st_mtime >= proto_file.stat().st_mtime
        and grpc_file.stat().st_mtime >= proto_file.stat().st_mtime
    ):
        return

    protoc.main(
        [
            "grpc_tools.protoc",
            f"-I{proto_dir}",
            f"--python_out={proto_dir}",
            f"--grpc_python_out={proto_dir}",
            str(proto_file),
        ]
    )

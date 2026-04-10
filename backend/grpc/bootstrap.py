from pathlib import Path

from grpc_tools import protoc


def ensure_generated() -> None:
    grpc_dir = Path(__file__).resolve().parent
    proto_file = grpc_dir / "fitness.proto"
    pb2_file = grpc_dir / "fitness_pb2.py"
    grpc_file = grpc_dir / "fitness_pb2_grpc.py"

    if pb2_file.exists() and grpc_file.exists():
        return

    protoc.main(
        [
            "grpc_tools.protoc",
            f"-I{grpc_dir}",
            f"--python_out={grpc_dir}",
            f"--grpc_python_out={grpc_dir}",
            str(proto_file),
        ]
    )

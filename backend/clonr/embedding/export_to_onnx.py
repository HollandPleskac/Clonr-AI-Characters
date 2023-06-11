import time
from pathlib import Path

from fire import Fire
from optimum.onnxruntime import ORTModelForFeatureExtraction, ORTOptimizer
from optimum.onnxruntime.configuration import OptimizationConfig

from clonr.embedding.encoder import ModelEnum
from clonr.utils import get_artifacts_dir


def get_onnx_dir():
    return get_artifacts_dir() / "onnx"


def export(model_name: ModelEnum, output_dir: str | None = None) -> Path:
    start = time.time()
    model_id = model_name.value
    output_dir = output_dir or model_id.split("/")[-1]
    onnx_path = get_onnx_dir() / output_dir

    print(f"Downloading {model_id} Pytorch and exporting to onnx")
    model = ORTModelForFeatureExtraction.from_pretrained(model_id, export=True)
    optimizer = ORTOptimizer.from_pretrained(model)
    optimization_config = OptimizationConfig(
        optimization_level=99
    )  # enable all optimizations

    print("Optimizing Graph")
    optimizer.optimize(
        save_dir=onnx_path,
        optimization_config=optimization_config,
    )

    print(
        f"Saved onnx version of {model_id} to {onnx_path}.\nTime: {time.time()-start:.02f}s"
    )
    return onnx_path


if __name__ == "__main__":
    Fire(export)

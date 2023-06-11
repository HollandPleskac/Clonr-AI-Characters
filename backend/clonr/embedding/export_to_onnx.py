import time
from pathlib import Path

from fire import Fire
from optimum.onnxruntime import ORTModelForFeatureExtraction, ORTOptimizer
from optimum.onnxruntime.configuration import OptimizationConfig

from clonr.embedding.encoder import ModelEnum
from clonr.utils import get_onnx_dir, get_transformers_dir


def export(model_name_or_dir: ModelEnum | str, output_dir: str | None = None) -> Path:
    start = time.time()

    if isinstance(model_name_or_dir, ModelEnum):
        model_id = model_name_or_dir.value
        if (path := (get_transformers_dir() / model_id.split("/")[-1])).exists():
            print(f"Found local copy of {model_id} in Artifacts dir.")
            model_id = str(path.resolve())
        else:
            print("Could not find local copy, will download from HF.")
    else:
        if not (path := Path(model_name_or_dir)).exists():
            raise FileNotFoundError(
                f"Could not locate directory at: {model_name_or_dir}."
            )
        model_id = path.name

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

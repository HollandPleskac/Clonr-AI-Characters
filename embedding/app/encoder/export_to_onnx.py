import time
from pathlib import Path

from fire import Fire
from loguru import logger
from optimum.onnxruntime import (
    ORTModelForFeatureExtraction,
    ORTModelForSequenceClassification,
    ORTOptimizer,
)
from optimum.onnxruntime.configuration import OptimizationConfig

from .encoder import CrossEncoderEnum, EmbeddingModelEnum
from .utils import get_onnx_dir, get_transformers_dir


def _export(model_name_or_dir: str, ORTClass, output_dir: str | None = None) -> Path:
    start = time.time()

    model_id = model_name_or_dir
    if (path := (get_transformers_dir() / model_id.split("/")[-1])).exists():
        logger.info(f"Found local copy of {model_id} in Artifacts dir.")
        model_id = str(path.resolve())
    else:
        logger.info("Could not find local transformers copy, will download from HF.")

    # Assumes a UNIX filesystem here, HF format is (...)/(...) for model names.
    output_dir = output_dir or model_id.split("/")[-1]
    onnx_path = get_onnx_dir() / output_dir

    logger.info(f"Downloading {model_id} Pytorch and exporting to onnx")
    model = ORTClass.from_pretrained(model_id, export=True)
    optimizer = ORTOptimizer.from_pretrained(model)
    optimization_config = OptimizationConfig(
        optimization_level=99
    )  # enable all optimizations

    logger.info("Optimizing Graph")
    optimizer.optimize(
        save_dir=onnx_path,
        optimization_config=optimization_config,
    )

    logger.info(
        f"✅ Saved onnx version of {model_id} to {onnx_path}.\nTime: {time.time()-start:.02f}s"
    )
    return onnx_path


def export(
    model_name_or_dir: str,
    output_dir: str | None = None,
) -> Path:
    try:
        _ = EmbeddingModelEnum(model_name_or_dir)
        return _export(
            model_name_or_dir=model_name_or_dir,
            ORTClass=ORTModelForFeatureExtraction,
            output_dir=output_dir,
        )
    except ValueError:
        pass
    try:
        _ = CrossEncoderEnum(model_name_or_dir)
        return _export(
            model_name_or_dir=model_name_or_dir,
            ORTClass=ORTModelForSequenceClassification,
            output_dir=output_dir,
        )
    except ValueError:
        pass
    raise ValueError(
        "Currently not accepting models not listed in the model Enums. If you want to override this behavior, please use the hidden _export function instead."
    )


if __name__ == "__main__":
    Fire(export)

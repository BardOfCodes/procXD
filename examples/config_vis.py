""" Visualize a configuration file using the SketchBuilder class."""

from yacs.config import CfgNode as CN
import networkx as nx
from procXD import SketchBuilder


def cfg_to_graph(cfg):
    """A helper function to convert a yacs config to a networkx graph.

    Args:
        cfg (yacs.config.CfgNode)

    Returns:
        nx_graph networkx.Digraph
    """
    nx_graph = nx.DiGraph()
    nodes_to_process = {"cfg": cfg}
    while nodes_to_process:
        current_name, current_node = nodes_to_process.popitem()
        content = [f'{current_name}.{k} = "{v}"' if isinstance(v, str) else
                   f'{current_name}.{k} = {v}' for k, v in current_node.items() 
                   if not isinstance(v, CN)]
        nx_graph.add_node(current_name, label=current_name, content=content)
        for key, value in current_node.items():
            if isinstance(value, CN):
                child_name = f'{current_name}.{key}'
                nx_graph.add_edge(current_name, child_name)
                nodes_to_process[child_name] = value
    return nx_graph


if __name__ == '__main__':
    # Create a dummy config:
    config = CN()
    config.EXPERIMENT = CN()
    config.EXPERIMENT.NAME = "NetworkAblation"
    config.EXPERIMENT.VERSION = "v1"
    config.EXPERIMENT.MACHINE = "CLUSTER"
    config.DATASET = CN()
    config.DATASET.NAME = "CIFAR10"
    config.DATASET.PATH = "/home/aditya/data/cifar10"
    config.DATASET.NUM_CLASSES = 5
    config.DATASET.CLASSES = ["airplane", "automobile", "bird", "cat", "deer"]
    config.DATASET.NUM_TRAIN = 50000
    config.TRAIN = CN()
    config.TRAIN.BATCH_SIZE = 128
    config.TRAIN.LOG_ITER = 100
    config.TRAIN.LOSSES = ["CE"]
    config.TRAIN.OPTIM = CN()
    config.TRAIN.OPTIM.TYPE = "SGD"
    config.TRAIN.OPTIM.LR = 0.1
    config.TRAIN.OPTIM.MOMENTUM = 0.9
    config.TRAIN.OPTIM.WEIGHT_DECAY = 5e-4
    config.MODEL = CN()
    config.MODEL.TYPE = "ResNet18"
    config.MODEL.INPUT_SIZE = 32
    config.MODEL.OUTPUT_SIZE = 10
    config.MODEL.DROPOUT = 0.2

    # To visualize, this convert it to a networkx graph:
    graph = cfg_to_graph(config)
    # now visualize with the sketch builder:
    SAVE_FILE = "examples/figures/configuration.excalidraw"
    sketch_builder = SketchBuilder(save_path=SAVE_FILE)
    sketch_builder.render_stack_sketch(graph, stacking="vertical")
    sketch_builder.export_to_file()
    del sketch_builder

    # Now compare clones with differences:
    config_A = config.clone()
    config_A.MODEL.OUTPUT_SIZE = 100
    config_A.MODEL.DROPOUT = 0.5
    config_B = config.clone()
    config_B.TRAIN.OPTIM = CN()
    config_B.TRAIN.OPTIM.TYPE = "ADAM"
    config_B.TRAIN.SCHEDULER = CN()
    config_B.TRAIN.SCHEDULER.TYPE = "CosineAnnealingLR"
    config_B.TRAIN.SCHEDULER.RATE = 0.1
    config_B.DATASET.NUM_CLASSES = 3
    config_B.DATASET.CLASSES = ["bird", "cat", "deer"]
    config_dict = {
        "config": cfg_to_graph(config),
        "config_A": cfg_to_graph(config_A),
        "config_B": cfg_to_graph(config_B)
    }
    SAVE_FILE = "examples/figures/config_comparison.excalidraw"
    sketch_builder = SketchBuilder(save_path=SAVE_FILE)
    sketch_builder.render_comparitive_stack_sketch(
        config_dict, base_config_name="config", stacking="vertical")
    # sketch_builder.render_comparitive_stack_sketch(
    #     config_dict, base_config_name="config", stacking="horizontal")
    sketch_builder.export_to_file()
    del sketch_builder

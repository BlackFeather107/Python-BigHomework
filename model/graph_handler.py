# model/graph_handler.py

from typing import List
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path
import math

# 解决matplotlib中文显示问题
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

from .similarity.result import ComparisonResult

class GraphHandler:
    """
    负责创建、绘制和导出抄袭关系网络图。
    """
    def create_graph(self, results: List[ComparisonResult], threshold: float = 0.8) -> nx.Graph:
        """
        根据查重结果和相似度阈值创建图。
        """
        graph = nx.Graph()
        
        all_files = set()
        for r in results:
            all_files.add(Path(r.file_a).name)
            all_files.add(Path(r.file_b).name)
        graph.add_nodes_from(list(all_files))

        for r in results:
            score = r.scores.get("综合可疑度", 0)
            if score >= threshold:
                file_a_name = Path(r.file_a).name
                file_b_name = Path(r.file_b).name
                graph.add_edge(file_a_name, file_b_name, weight=score)
        
        return graph

    def draw_graph(self, graph: nx.Graph, output_path: str = None):
        """
        绘制图形，采用分层布局优化视觉效果。
        """
        if not graph.nodes():
            print("图中没有节点，无法绘制。")
            return False # 返回布尔值以方便controller判断

        plt.figure(figsize=(12, 8))
        
        # 找出所有独立的“抄袭小组”（连通分量）
        components = list(nx.connected_components(graph))
        
        if not components:
            pos = {}
        else:
            num_components = len(components)
            cols = math.ceil(math.sqrt(num_components))
            rows = math.ceil(num_components / cols)
            
            final_pos = {}
            grid_x, grid_y = 0, rows - 1 # 从左上角开始排列
            
            for component in components:
                subgraph = graph.subgraph(component)
                pos_sub = nx.spring_layout(subgraph, k=0.8, iterations=50) 
                
                for node, (x, y) in pos_sub.items():
                    final_pos[node] = (x + grid_x * 2.5, y + grid_y * 2.5)
                
                # 更新下一个网格位置
                grid_x += 1
                if grid_x >= cols:
                    grid_x = 0
                    grid_y -= 1
            pos = final_pos

        # 绘制节点
        nx.draw_networkx_nodes(graph, pos, node_color='skyblue', node_size=1000)
        
        # 绘制节点标签
        nx.draw_networkx_labels(graph, pos, font_size=10, font_family='sans-serif')
        
        # 绘制边
        edges = graph.edges(data=True)
        if edges:
            edge_colors = [d['weight'] for u, v, d in edges]
            nx.draw_networkx_edges(graph, pos, width=2, edge_color=edge_colors, 
                                   edge_cmap=plt.cm.coolwarm, edge_vmin=0.8, edge_vmax=1.0)

        plt.title("抄袭关系网络图", size=20)
        plt.axis('off')

        if output_path:
            try:
                plt.savefig(output_path, bbox_inches='tight', dpi=150)
                plt.close()
                return True
            except Exception as e:
                print(f"导出图形失败: {e}")
                plt.close()
                return False
        else:
            plt.show()
            return True

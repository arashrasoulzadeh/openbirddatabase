'use client';

import { useState } from 'react';
import { Species } from '@/lib/types';

interface TaxonomyTreeProps {
  tree: any;
  onSelect: (species: Species) => void;
}

interface TreeNode {
  name: string;
  children?: Record<string, TreeNode>;
  species?: Species[];
  level: number;
}

export default function TaxonomyTree({ tree, onSelect }: TaxonomyTreeProps) {
  const [expanded, setExpanded] = useState<Set<string>>(new Set(['Passeriformes']));

  const toggleExpand = (path: string) => {
    setExpanded(prev => {
      const next = new Set(prev);
      if (next.has(path)) next.delete(path);
      else next.add(path);
      return next;
    });
  };

  const buildTree = (treeData: any): TreeNode[] => {
    if (!treeData) return [];
    
    const nodes: TreeNode[] = [];
    for (const [orderName, families] of Object.entries(treeData as Record<string, any>)) {
      const familyNodes: TreeNode[] = [];
      for (const [familyName, genera] of Object.entries(families as Record<string, any>)) {
        const genusNodes: TreeNode[] = [];
        for (const [genusName, speciesList] of Object.entries(genera as Record<string, any>)) {
          genusNodes.push({
            name: genusName,
            species: speciesList,
            level: 3,
          });
        }
        familyNodes.push({
          name: familyName,
          children: Object.fromEntries(genusNodes.map(g => [g.name, g])),
          level: 2,
        });
      }
      nodes.push({
        name: orderName,
        children: Object.fromEntries(familyNodes.map(f => [f.name, f])),
        level: 1,
      });
    }
    return nodes;
  };

  const renderNode = (node: TreeNode, path: string) => {
    const isExpanded = expanded.has(path);
    const hasChildren = node.children && Object.keys(node.children).length > 0;
    const speciesCount = node.species?.length || 0;

    if (node.species && node.species.length > 0) {
      // This is a genus with species
      return (
        <details open={isExpanded} onToggle={() => toggleExpand(path)} className="group">
          <summary className="flex items-center gap-2 py-1 px-2 cursor-pointer select-none">
            <span className="text-sm font-medium text-gray-700 group-hover:text-gray-900">
              {node.name} <span className="text-xs text-gray-400">({speciesCount})</span>
            </span>
          </summary>
          <div className="ml-4 mt-1 space-y-1 border-l border-gray-200 pl-2">
            {node.species.map((sp: Species) => (
              <button
                key={sp.id}
                onClick={() => onSelect(sp)}
                className="w-full text-left py-1 px-2 text-sm text-gray-600 hover:bg-gray-50 hover:text-gray-900 rounded transition-colors flex items-center gap-2"
              >
                <span className="font-italic text-gray-700">{sp.scientific}</span>
                {sp.common_fa && <span className="text-gray-500 text-xs font-vazir" dir="rtl">({sp.common_fa})</span>}
                {sp.common_en && <span className="text-gray-500 text-xs">({sp.common_en})</span>}
              </button>
            ))}
          </div>
        </details>
      );
    }

    if (hasChildren) {
      return (
        <details open={isExpanded} onToggle={() => toggleExpand(path)} className="group">
          <summary className="flex items-center gap-2 py-1 px-2 cursor-pointer select-none">
            <span className="font-medium text-gray-700 group-hover:text-gray-900">{node.name}</span>
          </summary>
          <div className="ml-4 mt-1 space-y-1 border-l border-gray-200 pl-2">
            {Object.entries(node.children as Record<string, TreeNode>).map(([name, child]) => (
              <div key={name}>{renderNode(child, `${path}/${name}`)}</div>
            ))}
          </div>
        </details>
      );
    }

    return null;
  };

  if (!tree) {
    return <div className="text-center py-12 text-gray-500">Loading taxonomy...</div>;
  }

  const treeNodes = buildTree(tree);

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <div className="p-4 border-b border-gray-200 bg-gray-50">
        <h2 className="text-lg font-semibold text-gray-900">Taxonomy Browser</h2>
        <p className="text-sm text-gray-500 mt-1">Click orders → families → genera → species</p>
      </div>
      <div className="p-4 space-y-2 max-h-[70vh] overflow-y-auto">
        {treeNodes.map(node => renderNode(node, node.name))}
      </div>
    </div>
  );
}
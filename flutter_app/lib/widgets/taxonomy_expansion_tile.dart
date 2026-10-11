import 'package:flutter/material.dart';
import 'package:openbird/models/species.dart';

class TaxonomyExpansionTile extends StatefulWidget {
  final TaxonomyNode node;
  final int level;
  final ValueChanged<String> onFamilyTap;

  const TaxonomyExpansionTile({
    super.key,
    required this.node,
    required this.level,
    required this.onFamilyTap,
  });

  @override
  State<TaxonomyExpansionTile> createState() => _TaxonomyExpansionTileState();
}

class _TaxonomyExpansionTileState extends State<TaxonomyExpansionTile> {
  bool _expanded = false;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isFamily = widget.node.rank == 'family';
    final isGenus = widget.node.rank == 'genus';
    final hasChildren = widget.node.children != null && widget.node.children!.isNotEmpty;

    if (isFamily && !hasChildren) {
      return _buildFamilyTile();
    }

    return Theme(
      data: theme.copyWith(dividerColor: Colors.transparent),
      child: ExpansionTile(
        initiallyExpanded: _expanded,
        onExpansionChanged: (expanded) => setState(() => _expanded = expanded),
        leading: _getLeadingIcon(),
        title: _buildTitle(),
        subtitle: widget.node.count != null
            ? Text('${widget.node.count} ${_getCountLabel()}')
            : null,
        children: hasChildren
            ? widget.node.children!.map((child) {
                return TaxonomyExpansionTile(
                  node: child,
                  level: widget.level + 1,
                  onFamilyTap: widget.onFamilyTap,
                );
              }).toList()
            : null,
        tilePadding: EdgeInsets.only(left: 16 + widget.level * 12, right: 16),
        childrenPadding: const EdgeInsets.only(left: 8, right: 8, bottom: 8),
      ),
    );
  }

  Widget _buildFamilyTile() {
    final theme = Theme.of(context);
    return Card(
      margin: EdgeInsets.only(
        left: 16 + widget.level * 12,
        right: 16,
        bottom: 4,
      ),
      child: ListTile(
        leading: const Icon(Icons.nest),
        title: Text(widget.node.name),
        subtitle: widget.node.count != null
            ? Text('${widget.node.count} species')
            : null,
        trailing: const Icon(Icons.chevron_right),
        onTap: () => widget.onFamilyTap(widget.node.name),
        contentPadding: EdgeInsets.only(left: 16 + widget.level * 12, right: 16),
      ),
    );
  }

  Widget _getLeadingIcon() {
    switch (widget.node.rank) {
      case 'order':
        return const Icon(Icons.account_tree);
      case 'family':
        return const Icon(Icons.folder);
      case 'genus':
        return const Icon(Icons.category);
      default:
        return const Icon(Icons.label);
    }
  }

  Widget _buildTitle() {
    final theme = Theme.of(context);
    return Text(
      widget.node.name,
      style: theme.textTheme.titleMedium?.copyWith(
        fontWeight: FontWeight.w600,
      ),
    );
  }

  String _getCountLabel() {
    switch (widget.node.rank) {
      case 'order': return 'families';
      case 'family': return 'species';
      case 'genus': return 'species';
      default: return 'items';
    }
  }
}
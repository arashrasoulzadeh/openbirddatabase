import { NextRequest, NextResponse } from 'next/server';
import { NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const order = searchParams.get('order');
    const family = searchParams.get('family');
    
    // Try to load from local index
    const fs = require('fs');
    const path = require('path');
    const indexPath = path.join(process.cwd(), '../../_index/taxonomy-tree.json');
    
    if (!fs.existsSync(indexPath)) {
      return NextResponse.json({ error: 'Taxonomy index not found' }, { status: 404 });
    }
    
    const taxonomyTree = JSON.parse(fs.readFileSync(indexPath, 'utf-8'));
    
    if (!order) {
      // Return all orders
      const orders = Object.keys(taxonomyTree).map(order => ({
        order,
        families: Object.keys(taxonomyTree[order]).length,
        species: Object.values(taxonomyTree[order]).reduce((sum: number, fam: any) => 
          sum + Object.values(fam).reduce((s: number, gen: any) => s + (gen.species?.length || 0), 0), 0)
      }));
      return NextResponse.json({ orders, total: Object.keys(taxonomyTree).length });
    }
    
    if (!family) {
      // Return families in order
      const families = Object.entries(taxonomyTree[order] || {}).map(([family, genera]) => ({
        family,
        genera: Object.keys(genera as object).length,
        species: Object.values(genera as object).reduce((sum: number, gen: any) => 
          sum + (gen.species?.length || 0), 0)
      }));
      return NextResponse.json({ order, families, total: families.length });
    }
    
    // Return species in family
    const genera = taxonomyTree[order]?.[family] || {};
    const species = Object.entries(genera).flatMap(([genus, speciesList]: [string, any]) => 
      (speciesList || []).map((sp: any) => ({ ...sp, genus }))
    );
    
    return NextResponse.json({ order, family, genera: Object.keys(genera), species, total: species.length });
  } catch (error) {
    console.error('Taxonomy API error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { q = '', filters, limit = 20, offset = 0, attributes } = body;

    // Forward to OpenBird API
    const apiUrl = process.env.OPENBIRD_API_URL || 'http://localhost:8000';
    
    const response = await fetch(`${apiUrl}/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ q, filters, limit, offset, attributes }),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Search API error:', error);
    
    // Fallback: try local JSON search
    try {
      const fs = require('fs');
      const path = require('path');
      const indexPath = path.join(process.cwd(), '../../_index/species-index.json');
      const speciesIndex = JSON.parse(fs.readFileSync(indexPath, 'utf-8'));
      
      const { q = '', limit = 20, offset = 0 } = await request.json();
      const qLower = q.toLowerCase();
      
      let results = speciesIndex;
      if (qLower) {
        results = results.filter((doc: any) => 
          doc.scientific_name?.toLowerCase().includes(qLower) ||
          doc.common_name_fa?.toLowerCase().includes(qLower) ||
          doc.common_name_en?.toLowerCase().includes(qLower) ||
          doc.order?.toLowerCase().includes(qLower) ||
          doc.family?.toLowerCase().includes(qLower) ||
          doc.genus?.toLowerCase().includes(qLower)
        );
      }
      
      const total = results.length;
      const hits = results.slice(offset, offset + limit);
      
      return NextResponse.json({ hits, total, limit, offset });
    } catch (fallbackError) {
      console.error('Fallback search error:', fallbackError);
      return NextResponse.json({ hits: [], total: 0, limit: 20, offset: 0 });
    }
  }
}
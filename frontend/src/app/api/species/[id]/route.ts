import { NextRequest, NextResponse } from 'next/server';

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = params;
    
    // Try to find species file
    const fs = require('fs');
    const path = require('path');
    
    // Search for the species file
    const birdsDir = path.join(process.cwd(), '../../birds');
    const files = fs.readdirSync(birdsDir, { recursive: true }) as string[];
    
    const speciesFile = files.find((f: string) => {
      const name = path.basename(f, '.md');
      // Match by scientific name slug
      return name.toLowerCase() === id.toLowerCase() || 
             f.toLowerCase().includes(id.toLowerCase());
    });
    
    if (!speciesFile) {
      return NextResponse.json({ error: 'Species not found' }, { status: 404 });
    }
    
    const filePath = path.join(birdsDir, speciesFile);
    const content = fs.readFileSync(filePath, 'utf-8');
    
    // Parse frontmatter
    if (!content.startsWith('---')) {
      return NextResponse.json({ error: 'Invalid file format' }, { status: 500 });
    }
    
    const parts = content.split('---', 3);
    if (parts.length < 3) {
      return NextResponse.json({ error: 'Invalid frontmatter' }, { status: 500 });
    }
    
    const yaml = require('js-yaml');
    const frontmatter = yaml.load(parts[1]);
    
    return NextResponse.json(frontmatter);
  } catch (error) {
    console.error('Species API error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
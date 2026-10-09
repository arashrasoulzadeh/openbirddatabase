#!/usr/bin/env python3
"""MCP Server for OpenBird Database - provides AI assistants access to bird data."""

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, Resource, EmbeddedResource
import mcp.types as types

DB_PATH = Path("exports/all_birds.sqlite")
SPECIES_DIR = Path("birds")
TRANSLATIONS_DIR = Path("translations")

app = Server("openbird-mcp")


def get_db_connection():
    """Get database connection."""
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found at {DB_PATH}. Run export first.")
    return sqlite3.connect(DB_PATH)


@app.list_tools()
async def list_tools() -> List[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="search_species",
            description="Search bird species by name, taxonomy, or traits",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query (scientific name, common name, Persian name)"},
                    "order": {"type": "string", "description": "Filter by taxonomic order"},
                    "family": {"type": "string", "description": "Filter by taxonomic family"},
                    "iucn_status": {"type": "string", "description": "Filter by IUCN status (LC, NT, VU, EN, CR, EW, EX)"},
                    "diet": {"type": "string", "description": "Filter by primary diet"},
                    "limit": {"type": "integer", "description": "Maximum results", "default": 20}
                },
                "required": []
            }
        ),
        Tool(
            name="get_species_detail",
            description="Get detailed information for a specific species",
            inputSchema={
                "type": "object",
                "properties": {
                    "scientific_name": {"type": "string", "description": "Scientific name of the species"},
                    "language": {"type": "string", "description": "Language for common names (en, fa, etc.)", "default": "en"}
                },
                "required": ["scientific_name"]
            }
        ),
        Tool(
            name="get_taxonomy_tree",
            description="Get hierarchical taxonomy tree",
            inputSchema={
                "type": "object",
                "properties": {
                    "order": {"type": "string", "description": "Filter by order"},
                    "family": {"type": "string", "description": "Filter by family"}
                },
                "required": []
            }
        ),
        Tool(
            name="get_species_by_location",
            description="Get species found in a specific geographic region",
            inputSchema={
                "type": "object",
                "properties": {
                    "region": {"type": "string", "description": "Geographic region (e.g., 'Iran', 'Middle East', 'Palearctic')"},
                    "limit": {"type": "integer", "description": "Maximum results", "default": 50}
                },
                "required": ["region"]
            }
        ),
        Tool(
            name="compare_species",
            description="Compare multiple species across traits",
            inputSchema={
                "type": "object",
                "properties": {
                    "species_list": {"type": "array", "items": {"type": "string"}, "description": "List of scientific names"},
                    "traits": {"type": "array", "items": {"type": "string"}, "description": "Traits to compare (e.g., morphology_body_mass_g, diet_primary)"}
                },
                "required": ["species_list"]
            }
        ),
        Tool(
            name="get_conservation_status",
            description="Get conservation statistics and species by IUCN status",
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {"type": "string", "description": "Specific IUCN status to filter"}
                },
                "required": []
            }
        ),
        Tool(
            name="get_field_statistics",
            description="Get statistical summaries for numerical fields",
            inputSchema={
                "type": "object",
                "properties": {
                    "field": {"type": "string", "description": "Field name (e.g., morphology_body_mass_g, morphology_wingspan_cm)"}
                },
                "required": ["field"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Execute MCP tool calls."""
    
    if name == "search_species":
        return await search_species(arguments)
    elif name == "get_species_detail":
        return await get_species_detail(arguments)
    elif name == "get_taxonomy_tree":
        return await get_taxonomy_tree(arguments)
    elif name == "get_species_by_location":
        return await get_species_by_location(arguments)
    elif name == "compare_species":
        return await compare_species(arguments)
    elif name == "get_conservation_status":
        return await get_conservation_status(arguments)
    elif name == "get_field_statistics":
        return await get_field_statistics(arguments)
    
    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def search_species(args: Dict[str, Any]) -> List[types.TextContent]:
    """Search species in database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = args.get("query", "")
    order = args.get("order")
    family = args.get("family")
    iucn_status = args.get("iucn_status")
    diet = args.get("diet")
    limit = args.get("limit", 20)
    
    sql = """
        SELECT names_scientific, names_en, names_fa, taxonomy_order, taxonomy_family,
               conservation_iucn_status, diet_primary, habitat_primary, morphology_body_mass_g
        FROM birds WHERE 1=1
    """
    params = []
    
    if query:
        sql += " AND (names_scientific LIKE ? OR names_en LIKE ? OR names_fa LIKE ?)"
        params.extend([f"%{query}%"] * 3)
    if order:
        sql += " AND taxonomy_order = ?"
        params.append(order)
    if family:
        sql += " AND taxonomy_family = ?"
        params.append(family)
    if iucn_status:
        sql += " AND conservation_iucn_status = ?"
        params.append(iucn_status)
    if diet:
        sql += " AND diet_primary = ?"
        params.append(diet)
    
    sql += f" ORDER BY names_scientific LIMIT {limit}"
    
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for row in rows:
        results.append({
            "scientific_name": row[0],
            "english_name": row[1],
            "persian_name": row[2],
            "order": row[3],
            "family": row[4],
            "iucn_status": row[5],
            "diet": row[6],
            "habitat": row[7],
            "body_mass_g": row[8]
        })
    
    return [TextContent(type="text", text=json.dumps(results, ensure_ascii=False, indent=2))]


async def get_species_detail(args: Dict[str, Any]) -> List[types.TextContent]:
    """Get detailed species information."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    scientific_name = args["scientific_name"]
    language = args.get("language", "en")
    
    cursor.execute("SELECT * FROM birds WHERE names_scientific = ?", (scientific_name,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return [TextContent(type="text", text=json.dumps({"error": "Species not found"}))]
    
    # Get column names
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM birds WHERE names_scientific = ?", (scientific_name,))
    cols = [desc[0] for desc in cursor.description]
    conn.close()
    
    species = dict(zip(cols, row))
    
    # Add translation if available
    if language != "en":
        trans_path = TRANSLATIONS_DIR / language / f"{scientific_name.replace(' ', '-').lower()}.md"
        if trans_path.exists():
            # Could parse translation file here
            species["translation_available"] = True
    
    return [TextContent(type="text", text=json.dumps(species, ensure_ascii=False, indent=2, default=str))]


async def get_taxonomy_tree(args: Dict[str, Any]) -> List[types.TextContent]:
    """Get taxonomy hierarchy."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    order = args.get("order")
    family = args.get("family")
    
    if family:
        cursor.execute("""
            SELECT DISTINCT taxonomy_order, taxonomy_family, taxonomy_genus, taxonomy_species, names_scientific
            FROM birds WHERE taxonomy_family = ?
            ORDER BY taxonomy_genus, taxonomy_species
        """, (family,))
    elif order:
        cursor.execute("""
            SELECT DISTINCT taxonomy_order, taxonomy_family, taxonomy_genus, taxonomy_species, names_scientific
            FROM birds WHERE taxonomy_order = ?
            ORDER BY taxonomy_family, taxonomy_genus, taxonomy_species
        """, (order,))
    else:
        cursor.execute("""
            SELECT DISTINCT taxonomy_order, taxonomy_family, taxonomy_genus, taxonomy_species, names_scientific
            FROM birds ORDER BY taxonomy_order, taxonomy_family, taxonomy_genus, taxonomy_species
        """)
    
    rows = cursor.fetchall()
    conn.close()
    
    # Build tree structure
    tree = {}
    for row in rows:
        order_name, family_name, genus, species, sci_name = row
        if order_name not in tree:
            tree[order_name] = {}
        if family_name not in tree[order_name]:
            tree[order_name][family_name] = {}
        if genus not in tree[order_name][family_name]:
            tree[order_name][family_name][genus] = []
        tree[order_name][family_name][genus].append({"species": species, "scientific_name": sci_name})
    
    return [TextContent(type="text", text=json.dumps(tree, ensure_ascii=False, indent=2))]


async def get_species_by_location(args: Dict[str, Any]) -> List[types.TextContent]:
    """Get species by geographic region."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    region = args["region"]
    limit = args.get("limit", 50)
    
    # Search in geographic distribution fields
    cursor.execute("""
        SELECT names_scientific, names_en, names_fa, taxonomy_order, taxonomy_family,
               conservation_iucn_status, geographic_range, geographic_realm
        FROM birds WHERE 
            geographic_range LIKE ? OR 
            geographic_realm LIKE ? OR
            names_en LIKE ? OR
            names_fa LIKE ?
        ORDER BY names_scientific LIMIT ?
    """, (f"%{region}%", f"%{region}%", f"%{region}%", f"%{region}%", limit))
    
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for row in rows:
        results.append({
            "scientific_name": row[0],
            "english_name": row[1],
            "persian_name": row[2],
            "order": row[3],
            "family": row[4],
            "iucn_status": row[5],
            "range": row[6],
            "realm": row[7]
        })
    
    return [TextContent(type="text", text=json.dumps(results, ensure_ascii=False, indent=2))]


async def compare_species(args: Dict[str, Any]) -> List[types.TextContent]:
    """Compare multiple species."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    species_list = args["species_list"]
    traits = args.get("traits", [
        "morphology_body_mass_g", "morphology_wingspan_cm", "morphology_length_cm",
        "diet_primary", "habitat_primary", "behavior_migration_status",
        "conservation_iucn_status", "reproduction_clutch_size"
    ])
    
    placeholders = ",".join(["?"] * len(species_list))
    cursor.execute(f"SELECT * FROM birds WHERE names_scientific IN ({placeholders})", species_list)
    rows = cursor.fetchall()
    conn.close()
    
    # Get column names
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM birds WHERE names_scientific IN ({placeholders})", species_list)
    cols = [desc[0] for desc in cursor.description]
    conn.close()
    
    comparison = {}
    for row in rows:
        species_data = dict(zip(cols, row))
        sci_name = species_data.get("names_scientific")
        comparison[sci_name] = {trait: species_data.get(trait) for trait in traits if trait in species_data}
    
    return [TextContent(type="text", text=json.dumps(comparison, ensure_ascii=False, indent=2, default=str))]


async def get_conservation_status(args: Dict[str, Any]) -> List[types.TextContent]:
    """Get conservation statistics."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    status = args.get("status")
    
    if status:
        cursor.execute("""
            SELECT names_scientific, names_en, names_fa, taxonomy_order, taxonomy_family,
                   conservation_population_trend, conservation_population_size
            FROM birds WHERE conservation_iucn_status = ?
            ORDER BY taxonomy_order, taxonomy_family
        """, (status,))
        rows = cursor.fetchall()
        conn.close()
        
        results = [{
            "scientific_name": r[0], "english_name": r[1], "persian_name": r[2],
            "order": r[3], "family": r[4], "population_trend": r[5], "population_size": r[6]
        } for r in rows]
    else:
        cursor.execute("""
            SELECT conservation_iucn_status, COUNT(*) as count
            FROM birds GROUP BY conservation_iucn_status ORDER BY count DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        
        results = {"summary": {r[0]: r[1] for r in rows}, "total": sum(r[1] for r in rows)}
    
    return [TextContent(type="text", text=json.dumps(results, ensure_ascii=False, indent=2))]


async def get_field_statistics(args: Dict[str, Any]) -> List[types.TextContent]:
    """Get statistics for a numerical field."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    field = args["field"]
    
    cursor.execute(f"""
        SELECT 
            MIN({field}), MAX({field}), AVG({field}), COUNT({field})
        FROM birds WHERE {field} IS NOT NULL
    """)
    row = cursor.fetchone()
    conn.close()
    
    if row[3] == 0:
        return [TextContent(type="text", text=json.dumps({"error": f"No data for field {field}"}))]
    
    stats = {
        "field": field,
        "min": row[0],
        "max": row[1],
        "mean": round(row[2], 2) if row[2] else None,
        "count": row[3]
    }
    
    return [TextContent(type="text", text=json.dumps(stats, ensure_ascii=False, indent=2))]


@app.list_resources()
async def list_resources() -> List[Resource]:
    """List available resources."""
    return [
        Resource(
            uri="openbird://database/info",
            name="Database Info",
            description="Information about the OpenBird database",
            mimeType="application/json"
        ),
        Resource(
            uri="openbird://taxonomy/orders",
            name="Taxonomic Orders",
            description="List of all taxonomic orders",
            mimeType="application/json"
        ),
        Resource(
            uri="openbird://taxonomy/families",
            name="Taxonomic Families",
            description="List of all taxonomic families",
            mimeType="application/json"
        )
    ]


@app.read_resource()
async def read_resource(uri: str) -> str:
    """Read a resource."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if uri == "openbird://database/info":
        cursor.execute("SELECT COUNT(*) FROM birds")
        total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(DISTINCT taxonomy_order) FROM birds")
        orders = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(DISTINCT taxonomy_family) FROM birds")
        families = cursor.fetchone()[0]
        conn.close()
        
        return json.dumps({
            "total_species": total,
            "total_orders": orders,
            "total_families": families,
            "data_sources": ["BirdNET", "BIRDBASE", "AVONICHE", "BirdFYI"],
            "languages": 434
        }, indent=2)
    
    elif uri == "openbird://taxonomy/orders":
        cursor.execute("SELECT DISTINCT taxonomy_order FROM birds ORDER BY taxonomy_order")
        orders = [r[0] for r in cursor.fetchall()]
        conn.close()
        return json.dumps(orders, indent=2)
    
    elif uri == "openbird://taxonomy/families":
        cursor.execute("SELECT DISTINCT taxonomy_family FROM birds ORDER BY taxonomy_family")
        families = [r[0] for r in cursor.fetchall()]
        conn.close()
        return json.dumps(families, indent=2)
    
    return json.dumps({"error": "Resource not found"})


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
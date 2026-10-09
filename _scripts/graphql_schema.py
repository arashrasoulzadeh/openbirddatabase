"""GraphQL schema for OpenBird API."""

import strawberry
from typing import Optional, List, Dict, Any
import json
from pathlib import Path
import sqlite3

DB_PATH = Path("exports/all_birds.sqlite")
INDEX_DIR = Path("_index")


@strawberry.type
class Species:
    scientific_name: str
    english_name: Optional[str] = None
    persian_name: Optional[str] = None
    order: Optional[str] = None
    family: Optional[str] = None
    genus: Optional[str] = None
    species: Optional[str] = None
    iucn_status: Optional[str] = None
    diet: Optional[str] = None
    habitat: Optional[str] = None
    body_mass_g: Optional[float] = None
    wingspan_cm: Optional[float] = None
    length_cm: Optional[float] = None
    migration_status: Optional[str] = None
    population_trend: Optional[str] = None
    clutch_size: Optional[float] = None
    data_quality: Optional[str] = None
    file_path: Optional[str] = None


@strawberry.type
class TaxonomyNode:
    name: str
    children: Optional[List["TaxonomyNode"]] = None
    species_count: Optional[int] = None
    species: Optional[List[Species]] = None


@strawberry.type
class SearchResult:
    hits: List[Species]
    total: int
    limit: int
    offset: int


@strawberry.type
class ConservationStats:
    status: str
    count: int


@strawberry.type
class FieldStats:
    field: str
    min: Optional[float] = None
    max: Optional[float] = None
    mean: Optional[float] = None
    count: int


@strawberry.type
class DatabaseInfo:
    total_species: int
    total_orders: int
    total_families: int
    data_sources: List[str]
    languages: int


@strawberry.type
class Query:
    @strawberry.field
    def search_species(
        self,
        query: str = "",
        order: Optional[str] = None,
        family: Optional[str] = None,
        iucn_status: Optional[str] = None,
        diet: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> SearchResult:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        sql = """
            SELECT names_scientific, names_en, names_fa, taxonomy_order, taxonomy_family,
                   taxonomy_genus, taxonomy_species, conservation_iucn_status, diet_primary,
                   habitat_primary, morphology_body_mass_g, morphology_wingspan_cm,
                   morphology_length_cm, behavior_migration_status, conservation_population_trend,
                   reproduction_clutch_size, data_quality, file_path
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
        
        sql += f" ORDER BY names_scientific LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        
        # Get total count
        count_sql = sql.replace(
            "SELECT names_scientific, names_en, names_fa, taxonomy_order, taxonomy_family, "
            "taxonomy_genus, taxonomy_species, conservation_iucn_status, diet_primary, "
            "habitat_primary, morphology_body_mass_g, morphology_wingspan_cm, "
            "morphology_length_cm, behavior_migration_status, conservation_population_trend, "
            "reproduction_clutch_size, data_quality, file_path",
            "SELECT COUNT(*)"
        ).split("ORDER BY")[0]
        cursor.execute(count_sql, params[:-2])
        total = cursor.fetchone()[0]
        conn.close()
        
        hits = []
        for row in rows:
            hits.append(Species(
                scientific_name=row[0],
                english_name=row[1],
                persian_name=row[2],
                order=row[3],
                family=row[4],
                genus=row[5],
                species=row[6],
                iucn_status=row[7],
                diet=row[8],
                habitat=row[9],
                body_mass_g=row[10],
                wingspan_cm=row[11],
                length_cm=row[12],
                migration_status=row[13],
                population_trend=row[14],
                clutch_size=row[15],
                data_quality=row[16],
                file_path=row[17]
            ))
        
        return SearchResult(hits=hits, total=total, limit=limit, offset=offset)
    
    @strawberry.field
    def get_species(self, scientific_name: str) -> Optional[Species]:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT names_scientific, names_en, names_fa, taxonomy_order, taxonomy_family,
                   taxonomy_genus, taxonomy_species, conservation_iucn_status, diet_primary,
                   habitat_primary, morphology_body_mass_g, morphology_wingspan_cm,
                   morphology_length_cm, behavior_migration_status, conservation_population_trend,
                   reproduction_clutch_size, data_quality, file_path
            FROM birds WHERE names_scientific = ?
        """, (scientific_name,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return Species(
            scientific_name=row[0],
            english_name=row[1],
            persian_name=row[2],
            order=row[3],
            family=row[4],
            genus=row[5],
            species=row[6],
            iucn_status=row[7],
            diet=row[8],
            habitat=row[9],
            body_mass_g=row[10],
            wingspan_cm=row[11],
            length_cm=row[12],
            migration_status=row[13],
            population_trend=row[14],
            clutch_size=row[15],
            data_quality=row[16],
            file_path=row[17]
        )
    
    @strawberry.field
    def taxonomy_tree(self, order: Optional[str] = None, family: Optional[str] = None) -> List[TaxonomyNode]:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        if family:
            cursor.execute("""
                SELECT taxonomy_order, taxonomy_family, taxonomy_genus, taxonomy_species, names_scientific
                FROM birds WHERE taxonomy_family = ?
                ORDER BY taxonomy_genus, taxonomy_species
            """, (family,))
        elif order:
            cursor.execute("""
                SELECT taxonomy_order, taxonomy_family, taxonomy_genus, taxonomy_species, names_scientific
                FROM birds WHERE taxonomy_order = ?
                ORDER BY taxonomy_family, taxonomy_genus, taxonomy_species
            """, (order,))
        else:
            cursor.execute("""
                SELECT taxonomy_order, taxonomy_family, taxonomy_genus, taxonomy_species, names_scientific
                FROM birds ORDER BY taxonomy_order, taxonomy_family, taxonomy_genus, taxonomy_species
            """)
        
        rows = cursor.fetchall()
        conn.close()
        
        # Build tree
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
        
        def build_node(name: str, data: Dict, level: int = 0) -> TaxonomyNode:
            if level == 0:  # Order level
                children = [build_node(fam, genuses, 1) for fam, genuses in data.items()]
                return TaxonomyNode(name=name, children=children)
            elif level == 1:  # Family level
                children = [build_node(gen, species_list, 2) for gen, species_list in data.items()]
                return TaxonomyNode(name=name, children=children)
            else:  # Genus level
                species_list = [Species(scientific_name=s["scientific_name"], species=s["species"]) for s in data]
                return TaxonomyNode(name=name, species=species_list, species_count=len(species_list))
        
        return [build_node(order_name, families) for order_name, families in tree.items()]
    
    @strawberry.field
    def conservation_status(self, status: Optional[str] = None) -> List[ConservationStats]:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        if status:
            cursor.execute("""
                SELECT conservation_iucn_status, COUNT(*)
                FROM birds WHERE conservation_iucn_status = ?
                GROUP BY conservation_iucn_status
            """, (status,))
        else:
            cursor.execute("""
                SELECT conservation_iucn_status, COUNT(*)
                FROM birds GROUP BY conservation_iucn_status ORDER BY COUNT(*) DESC
            """)
        
        rows = cursor.fetchall()
        conn.close()
        
        return [ConservationStats(status=row[0] or "Unknown", count=row[1]) for row in rows]
    
    @strawberry.field
    def field_statistics(self, field: str) -> Optional[FieldStats]:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(f"""
            SELECT MIN({field}), MAX({field}), AVG({field}), COUNT({field})
            FROM birds WHERE {field} IS NOT NULL
        """)
        row = cursor.fetchone()
        conn.close()
        
        if row[3] == 0:
            return None
        
        return FieldStats(
            field=field,
            min=row[0],
            max=row[1],
            mean=round(row[2], 2) if row[2] else None,
            count=row[3]
        )
    
    @strawberry.field
    def database_info(self) -> DatabaseInfo:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM birds")
        total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(DISTINCT taxonomy_order) FROM birds")
        orders = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(DISTINCT taxonomy_family) FROM birds")
        families = cursor.fetchone()[0]
        conn.close()
        
        return DatabaseInfo(
            total_species=total,
            total_orders=orders,
            total_families=families,
            data_sources=["BirdNET", "BIRDBASE", "AVONICHE", "BirdFYI"],
            languages=434
        )
    
    @strawberry.field
    def compare_species(self, species_list: List[str], traits: Optional[List[str]] = None) -> str:
        """Returns JSON string of comparison data."""
        import json
        if not traits:
            traits = [
                "morphology_body_mass_g", "morphology_wingspan_cm", "morphology_length_cm",
                "diet_primary", "habitat_primary", "behavior_migration_status",
                "conservation_iucn_status", "reproduction_clutch_size"
            ]
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        placeholders = ",".join(["?"] * len(species_list))
        cursor.execute(f"SELECT * FROM birds WHERE names_scientific IN ({placeholders})", species_list)
        rows = cursor.fetchall()
        
        cursor.execute(f"SELECT * FROM birds WHERE names_scientific IN ({placeholders})", species_list)
        cols = [desc[0] for desc in cursor.description]
        conn.close()
        
        comparison = {}
        for row in rows:
            species_data = dict(zip(cols, row))
            sci_name = species_data.get("names_scientific")
            comparison[sci_name] = {trait: species_data.get(trait) for trait in traits if trait in species_data}
        
        return json.dumps(comparison, ensure_ascii=False, indent=2, default=str)


schema = strawberry.Schema(query=Query)
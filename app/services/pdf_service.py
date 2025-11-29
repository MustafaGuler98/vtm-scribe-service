import io
import os
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject

class PdfService:
    """
    Service responsible for handling PDF manipulations in-memory.
    It maps the character data to the specific AcroForm fields of the V20 character sheet.
    """

    def __init__(self, template_path: str):
        self.template_path = template_path

    def _calculate_dots(self, start_index: int, value: int, block_size: int = 8) -> dict:
        """
        Calculates the visual 'dots' for attributes, abilities, and disciplines.
        
        Args:
            start_index (int): The starting field ID for the trait.
            value (int): The character's rating in the trait (1-10).
            block_size (int): The number of dots in a visual block (default 8).
            
        Returns:
            dict: A dictionary of field names and their activation status (/Yes or /Off).
        """
        dot_data = {}
        
        try:
            val = int(value)
        except (ValueError, TypeError):
            val = 0


        normal_limit = min(val, block_size)
        
        for i in range(block_size):
            key = f"dot{start_index + i}"
            dot_data[key] = NameObject("/Yes") if i < normal_limit else NameObject("/Off")
            
        # If value is 9+, the 8th dot gets a special suffix field (e.g., dot8a)
        # I dont know why it is like this, i mapped the pdf and this was the result.
        end_of_block_id = start_index + block_size - 1
        suffix_key = f"dot{end_of_block_id}a"
        
        # Activate suffix only if value exceeds the standard block size
        dot_data[suffix_key] = NameObject("/Yes") if val > block_size else NameObject("/Off")
        
        return dot_data

    def _calculate_virtues(self, start_index: int, value: int) -> dict:
        """
        Calculates dots for Virtues.
        Virtues use a visual block of 5.
        """
        dot_data = {}
        try:
            val = int(value)
        except (ValueError, TypeError):
            val = 1 # Virtues start at 1 and capped at 5
        val = min(val, 5)

        for i in range(5):
            key = f"dot{start_index + i}"
            dot_data[key] = NameObject("/Yes") if i < val else NameObject("/Off")
        
        return dot_data

    def _calculate_tracker(self, prefix: str, value: int, max_slots: int = 10) -> dict:
        """
        Calculates simple linear trackers like Willpower and Humanity.
        Field keys format: {prefix}1, {prefix}2, ... (e.g., willdot1, hdot1)
        """
        dot_data = {}
        try:
            val = int(value)
        except (ValueError, TypeError):
            val = 0

        for i in range(1, max_slots + 1):
            key = f"{prefix}{i}"
            dot_data[key] = NameObject("/Yes") if i <= val else NameObject("/Off")
        
        return dot_data

    def generate_character_stream(self, char_data: dict) -> io.BytesIO:
        """
        Generates a filled PDF character sheet in-memory.
        
        Args:
            char_data (dict): Dictionary containing character properties.
            
        Returns:
            io.BytesIO: An in-memory binary stream of the filled PDF.
        """
        if not os.path.exists(self.template_path):
            raise FileNotFoundError(f"Template not found at: {self.template_path}")

        reader = PdfReader(self.template_path)
        writer = PdfWriter()
        writer.append(reader)

        form_fields = {}

        # --- TEXT FIELDS MAPPING ---
        # Maps incoming JSON keys to PDF AcroForm field names.
        
        # --- OVERFLOW LOGIC ---
        # There is only 6 slots for disciplines and backgrounds.
        # We use other section for the overflowing disciplines and backgrounds.

        disciplines = char_data.get("disciplines", {})
        sorted_discs = sorted(disciplines.items(), key=lambda x: x[1], reverse=True)
        
        backgrounds = char_data.get("backgrounds", {})
        sorted_backs = sorted(backgrounds.items(), key=lambda x: x[1], reverse=True)

        main_disciplines = sorted_discs[:6]
        overflow_disciplines = sorted_discs[6:]

        main_backgrounds = sorted_backs[:6]
        overflow_backgrounds = sorted_backs[6:]

        # Prepare lines for the 'Other' section (misc fields)
        other_lines = []
        other_lines.append("OTHER TRAITS") 
        other_lines.append("") # Empty line for spacing
        
        if overflow_disciplines:
            other_lines.append("--- Additional Disciplines ---")
            for name, val in overflow_disciplines:
                other_lines.append(f"{name.title().replace('_', ' ')}: {val}")
            other_lines.append("")

        if overflow_backgrounds:
            other_lines.append("--- Additional Backgrounds ---")
            for name, val in overflow_backgrounds:
                other_lines.append(f"{name.title().replace('_', ' ')}: {val}")
            other_lines.append("")

        # Map the lines to specific PDF fields (misc1, misc2... misc13)
        for i, line in enumerate(other_lines):
            if i < 13: # The sheet has approximately 13 misc lines
                form_fields[f"misc{i+1}"] = line

        # --- TEXT MAPPING ---
        text_mapping = {
            "name": char_data.get("name", ""),
            "player": char_data.get("player", ""),
            "chronicle": char_data.get("chronicle", ""),
            "nature": char_data.get("nature", {}).get("name", "") if isinstance(char_data.get("nature"), dict) else str(char_data.get("nature", "")),
            "demeanor": char_data.get("demeanor", {}).get("name", "") if isinstance(char_data.get("demeanor"), dict) else str(char_data.get("demeanor", "")),
            "concept": char_data.get("concept", {}).get("name", "") if isinstance(char_data.get("concept"), dict) else str(char_data.get("concept", "")),
            "Clan": char_data.get("clan", {}).get("name", "") if isinstance(char_data.get("clan"), dict) else str(char_data.get("clan", "")),
            "gen": str(char_data.get("generation", "")),
            "sire": char_data.get("sire", ""),
            "ppt": str(char_data.get("bloodPointsPerTurn", "")),
            "weakness": char_data.get("clan", {}).get("weakness", "") if isinstance(char_data.get("clan"), dict) else "",
            "experience": f"{char_data.get('spentExperience', 0)}/{char_data.get('totalExperience', 0)}",
            
            # Intentionally left empty, new title is in misc1 now.
            # Original misctitle area is bugged.
            "misctitle": " "
        }
        form_fields.update(text_mapping)


        # --- ATTRIBUTES (Block Size: 8) ---
        # The PDF uses specific start IDs for each attribute block.
        # Order: Strength(1), Dexterity(9), Stamina(17), Charisma(25), etc.
        attr_order = [
            "strength", "dexterity", "stamina", 
            "charisma", "manipulation", "appearance", 
            "perception", "intelligence", "wits"
        ]
        
        attributes = char_data.get("attributes", {})
        for i, attr_name in enumerate(attr_order):
            val = attributes.get(attr_name, 1)
            start_id = 1 + (i * 8)
            form_fields.update(self._calculate_dots(start_id, val))

        # --- ABILITIES (Block Size: 8) ---
        # Alertness starts at ID 73.
        # Order must match the PDF column flow: Talents -> Skills -> Knowledges
        ability_order = [
            # Talents
            "alertness", "athletics", "awareness", "brawl", "empathy", 
            "expression", "intimidation", "leadership", "streetwise", "subterfuge",
            # Skills
            "animal_ken", "crafts", "drive", "etiquette", "firearms", 
            "larceny", "melee", "performance", "stealth", "survival",
            # Knowledges
            "academics", "computer", "finance", "investigation", "law", 
            "medicine", "occult", "politics", "science", "technology"
        ]
        
        abilities = char_data.get("abilities", {})
        for i, abil_name in enumerate(ability_order):
            val = abilities.get(abil_name, 0)
            start_id = 73 + (i * 8)
            form_fields.update(self._calculate_dots(start_id, val))

       # --- 4. DISCIPLINES (Main Slots) ---
        # Only the first 6 disciplines are mapped to the visual dots.
        for i, (name, val) in enumerate(main_disciplines):
            form_fields[f"disciplines{i+1}"] = name.title().replace("_", " ")
            start_id = 313 + (i * 8)
            form_fields.update(self._calculate_dots(start_id, val))

        # --- 5. BACKGROUNDS (Main Slots) ---
        # Only the first 6 backgrounds are mapped to the visual dots.
        for i, (name, val) in enumerate(main_backgrounds):
            form_fields[f"back{i+1}"] = name.title().replace("_", " ")
            start_id = 361 + (i * 8)
            form_fields.update(self._calculate_dots(start_id, val))

        # --- VIRTUES (Block Size: 5) ---
        # Start ID: 409. Order: Conscience, Self-Control, Courage.
        virtues = char_data.get("virtues", {})
        
        # Conscience (ID 409)
        form_fields.update(self._calculate_virtues(409, virtues.get("conscience", 1)))
        # Self-Control (ID 414)
        form_fields.update(self._calculate_virtues(414, virtues.get("self_control", 1)))
        # Courage (ID 419)
        form_fields.update(self._calculate_virtues(419, virtues.get("courage", 1)))

        # --- TRACKERS ---
        # Humanity (hdot1 - hdot10)
        form_fields.update(self._calculate_tracker("hdot", char_data.get("humanity", 7)))
        # Willpower (willdot1 - willdot10)
        form_fields.update(self._calculate_tracker("willdot", char_data.get("willpower", 6)))

        # --- WRITE & STREAM ---
        # Update fields in the PDF page
        writer.update_page_form_field_values(
            writer.pages[0], 
            form_fields,
            auto_regenerate=False
        )

        # Create an in-memory byte stream
        output_stream = io.BytesIO()
        writer.write(output_stream)
        
        # Reset pointer to the beginning so it can be read
        output_stream.seek(0) 
        
        return output_stream
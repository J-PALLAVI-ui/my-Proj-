import sqlite3

def run_db_audit():
    conn = sqlite3.connect('fujinova.db')
    c = conn.cursor()

    c.execute('SELECT COUNT(*) FROM places;')
    total = c.fetchone()[0]

    c.execute('SELECT place_id, COUNT(*) FROM places GROUP BY place_id HAVING COUNT(*) > 1;')
    duplicates = c.fetchall()

    c.execute('''
        SELECT place_id FROM places 
        WHERE latitude IS NULL OR longitude IS NULL 
           OR latitude < 35.0 OR latitude > 36.0 
           OR longitude < 138.0 OR longitude > 139.5;
    ''')
    bad_coords = c.fetchall()

    c.execute('''
        SELECT place_id FROM places 
        WHERE required_attribution IS NULL OR trim(required_attribution) = ''
           OR source_url IS NULL OR trim(source_url) = '';
    ''')
    bad_attrib = c.fetchall()

    c.execute('''
        SELECT place_id, general_admission_type, general_admission_fee_jpy FROM places 
        WHERE (general_admission_type = 'FREE' AND general_admission_fee_jpy IS NOT NULL AND general_admission_fee_jpy > 0) 
           OR (general_admission_type = 'PAID' AND (general_admission_fee_jpy IS NULL OR general_admission_fee_jpy <= 0));
    ''')
    bad_fees = c.fetchall()

    c.execute('''
        SELECT place_id, accessibility_status, accessibility_evidence FROM places 
        WHERE accessibility_evidence IS NULL OR trim(accessibility_evidence) = '';
    ''')
    bad_access = c.fetchall()

    print(f"TOTAL_PLACES: {total}")
    print(f"DUPLICATES: {len(duplicates)}")
    print(f"BAD_COORDS: {len(bad_coords)}")
    print(f"BAD_ATTRIB: {len(bad_attrib)}")
    print(f"BAD_FEES: {len(bad_fees)}")
    print(f"BAD_ACCESS: {len(bad_access)}")

if __name__ == '__main__':
    run_db_audit()

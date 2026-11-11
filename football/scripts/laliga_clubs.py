"""Club name normalisation and stadium coordinates (approximate, stadium city) for LALIGA clubs 2015-2027."""
NAMES = {'Club Atlético de Madrid': 'Atlético Madrid', 'CD Alavés': 'Alavés', 'Deportivo Alavés': 'Alavés', 'RC Deportivo La Coruña': 'Deportivo', 'Deportivo La Coruña': 'Deportivo',
         'Espanyol Barcelona': 'Espanyol', 'RCD Espanyol de Barcelona': 'Espanyol', 'RC Celta de Vigo': 'Celta', 'RC Celta': 'Celta', 'Rayo Vallecano de Madrid': 'Rayo Vallecano',
         'Real Betis Balompié': 'Real Betis', 'Real Madrid CF': 'Real Madrid', 'Real Sociedad de Fútbol': 'Real Sociedad', 'Real Valladolid CF': 'Valladolid', 'Real Valladolid': 'Valladolid',
         'CA Osasuna': 'Osasuna', 'CD Leganés': 'Leganés', 'Cádiz CF': 'Cádiz', 'Elche CF': 'Elche', 'Getafe CF': 'Getafe', 'Girona FC': 'Girona', 'Granada CF': 'Granada',
         'Levante UD': 'Levante', 'Málaga CF': 'Málaga', 'RCD Mallorca': 'Mallorca', 'Real Racing Club de Santander': 'Racing Santander', 'SD Eibar': 'Eibar', 'SD Huesca': 'Huesca',
         'Sevilla FC': 'Sevilla', 'Sporting Gijón': 'Sporting Gijón', 'UD Almería': 'Almería', 'UD Las Palmas': 'Las Palmas', 'Valencia CF': 'Valencia', 'Villarreal CF': 'Villarreal',
         'FC Barcelona': 'Barcelona', 'Athletic Club': 'Athletic Club', 'Real Oviedo': 'Real Oviedo'}
COORDS = {'Athletic Club': (43.264, -2.949), 'Atlético Madrid': (40.436, -3.599), 'Osasuna': (42.797, -1.637), 'Alavés': (42.837, -2.688), 'Leganés': (40.340, -3.760),
          'Cádiz': (36.502, -6.273), 'Deportivo': (43.369, -8.417), 'Elche': (38.267, -0.663), 'Espanyol': (41.348, 2.076), 'Barcelona': (41.381, 2.123), 'Getafe': (40.326, -3.715),
          'Girona': (41.961, 2.829), 'Granada': (37.153, -3.596), 'Levante': (39.495, -0.364), 'Málaga': (36.734, -4.426), 'Celta': (42.212, -8.740), 'Mallorca': (39.590, 2.630),
          'Rayo Vallecano': (40.392, -3.659), 'Real Betis': (37.356, -5.982), 'Real Madrid': (40.453, -3.688), 'Real Oviedo': (43.361, -5.870), 'Racing Santander': (43.476, -3.794),
          'Real Sociedad': (43.301, -1.974), 'Valladolid': (41.645, -4.761), 'Eibar': (43.182, -2.476), 'Huesca': (42.131, -0.425), 'Sevilla': (37.384, -5.971),
          'Sporting Gijón': (43.536, -5.637), 'Almería': (36.840, -2.435), 'Las Palmas': (28.100, -15.457), 'Valencia': (39.475, -0.358), 'Villarreal': (39.944, -0.104)}

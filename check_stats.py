import sys
sys.path.insert(0, '.')
from app import app
from flask import render_template

with app.app_context():
    from models.models import User
    user = User.query.first()
    if not user:
        print('Nenhum usuario encontrado')
        sys.exit(1)
    
    from flask_login import login_user
    with app.test_request_context('/listar_atividades'):
        login_user(user)
        
        html = render_template('listar_atividades.html', atividades=[])
        
        # Extract just the stats section
        import re
        stats_match = re.search(r'<div class="stats-atividades">.*?</div>\s*</div>', html, re.DOTALL)
        if stats_match:
            stats_html = stats_match.group(0)
            print('Stats section HTML:')
            print(stats_html)
        else:
            print('Stats section not found')
            
        # Check for stat-card class
        stat_cards = re.findall(r'class="stat-card[^"]*"', html)
        print(f'\nStat card classes: {stat_cards}')
        
        # Check for total-horas id
        if 'id="total-horas"' in html:
            print('\nFound id="total-horas"')
        else:
            print('\nid="total-horas" NOT found')

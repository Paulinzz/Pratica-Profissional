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
        
        # Check for stat cards
        import re
        stat_icons = re.findall(r'<div class="stat-icon"[^>]*>.*?</div>', html, re.DOTALL)
        print(f'Stat icons found: {len(stat_icons)}')
        for i, icon in enumerate(stat_icons):
            print(f'  Icon {i+1}: {icon[:120]}...')
        
        has_total_horas = 'total-horas' in html
        print(f'Has total-horas id: {has_total_horas}')
        
        has_clock = 'fa-clock' in html
        print(f'Has clock icon: {has_clock}')

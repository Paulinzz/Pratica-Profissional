from app import app, db

# Criar tabelas
with app.app_context():
    try:
        db.create_all()
        print("✅ Tabelas criadas com sucesso!")
        
        # Verificar quais tabelas foram criadas
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tabelas = inspector.get_table_names()
        
        print(f"📋 Tabelas criadas: {tabelas}")
        
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
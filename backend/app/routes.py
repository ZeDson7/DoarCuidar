"""
Este módulo define as rotas para o aplicativo Flask.
"""
import logging
from flask import render_template, request, redirect, url_for, session, flash
from app import app
from app.consulta_empresas import buscar_empresas
from app.models import db, Usuario, Donatario
from werkzeug.security import generate_password_hash, check_password_hash

logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def index():
    """Página inicial do site."""
    return render_template('index.html')  # Renderiza o formulário de pesquisa


@app.route('/pesquisar', methods=['POST'])
def pesquisar():
    logging.debug("Iniciando a rota /pesquisar")
    client_id = "SEU_CLIENT_ID"
    client_secret = "SEU_SECRET"
    palavra_chave = request.form.get('palavra_chave')  # Obtém a palavra-chave do formulário
    estado = request.form.get('estado')  # Obtém o estado do formulário

    if not client_id or not client_secret:
        erro = "Credenciais de autenticação não configuradas."
        logging.error(erro)
        return render_template('resultados.html', erro=erro)

    try:
        logging.debug(f"Buscando empresas com palavra-chave: {palavra_chave}, estado: {estado}")
        empresas = buscar_empresas(client_id, client_secret, palavra_chave, estado)
        empresas = resultado['empresas']
        return render_template('resultados.html', empresas=empresas)
    except Exception as e:
        logging.error(f"Erro ao buscar empresas: {str(e)}")
        return render_template('resultados.html', erro="Erro interno no servidor.")


from flask import session, redirect, url_for, flash

@app.route('/buscar_instituicoes', methods=['GET', 'POST'])
def buscar_instituicoes():
    if 'usuario_id' not in session:
        flash('Você precisa estar logado para pesquisar instituições.')
        return redirect(url_for('login'))
    if request.method == 'POST':
        palavra_chave = request.form['palavra_chave']
        estado = request.form['estado']
        resultado = buscar_empresas('', '', palavra_chave, estado)
        empresas = resultado['empresas']
        return render_template('resultados.html', empresas=empresas)
    # Para GET ou outros casos, sempre retorne algo:
    return render_template('resultados.html', empresas=[])


@app.route('/cadastro', methods=['GET'])
def cadastro():
    return render_template('cadastro.html')


def validar_cpf(cpf):
    cpf = ''.join(filter(str.isdigit, cpf))
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    for i in range(9, 11):
        soma = sum(int(cpf[num]) * ((i+1) - num) for num in range(0, i))
        digito = ((soma * 10) % 11) % 10
        if digito != int(cpf[i]):
            return False
    return True

@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    nome = request.form['nome']
    cpf = request.form['cpf']
    email = request.form['email']
    senha = generate_password_hash(request.form['senha'])

    if not validar_cpf(cpf):
        flash('CPF inválido.')
        return redirect(url_for('cadastro'))

    if Usuario.query.filter_by(email=email).first():
        flash('E-mail já cadastrado. Faça login ou use outro e-mail.')
        return redirect(url_for('cadastro'))

    if Usuario.query.filter_by(cpf=cpf).first():
        flash('CPF já cadastrado. Faça login ou use outro CPF.')
        return redirect(url_for('cadastro'))

    usuario = Usuario(nome=nome, cpf=cpf, email=email, senha=senha)
    db.session.add(usuario)
    db.session.commit()
    session['usuario_id'] = usuario.id
    return redirect(url_for('perfil'))


@app.route('/perfil')
def perfil():
    usuario_id = session.get('usuario_id')
    if not usuario_id:
        return redirect(url_for('login'))
    usuario = Usuario.query.get(usuario_id)
    donatarios = Donatario.query.filter_by(usuario_id=usuario_id).all()
    return render_template('perfil.html', usuario=usuario, donatarios=donatarios)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and check_password_hash(usuario.senha, senha):
            session['usuario_id'] = usuario.id
            return redirect(url_for('perfil'))
        else:
            flash('E-mail ou senha inválidos.')
            return redirect(url_for('login'))
    return render_template('login.html')


from flask import request, session, redirect, url_for, flash
from app.models import Donatario, db

@app.route('/salvar_instituicao', methods=['POST'])
def salvar_instituicao():
    if 'usuario_id' not in session:
        flash('Você precisa estar logado para salvar instituições.')
        return redirect(url_for('login'))
    nome = request.form['nome']
    cnpj = request.form['cnpj']
    telefone = request.form['telefone']
    endereco = request.form['endereco']
    usuario_id = session['usuario_id']

    donatario = Donatario(
        usuario_id=usuario_id,
        nome=nome,
        cnpj=cnpj,
        telefone=telefone,
        endereco=endereco
    )
    db.session.add(donatario)
    db.session.commit()
    flash('Instituição salva com sucesso!')
    return redirect(url_for('perfil'))
import os
from flask import Flask, render_template, request, redirect, url_for
import uuid
from datetime import date

app = Flask(__name__)

backlog_file = 'backlog.txt'
# Lista de opções de urgência
urgencia_opcoes = {
    '0': 'TBC',
    '1': 'Não Prioritária',
    '2': 'Baixa Prioridade',
    '3': 'Média Prioridade',
    '4': 'Alta Prioridade',
    '5': 'Elevada Prioridade'
}

tarefas = []

# Garantir que o arquivo backlog.txt existe
if not os.path.exists(backlog_file):
    open(backlog_file, 'w').close()

@app.route('/')
def index():
    tarefas_pendentes = [tarefa for tarefa in tarefas if not tarefa['concluida']]
    tarefas_concluidas = [tarefa for tarefa in tarefas if tarefa['concluida']]
    return render_template('index.html', tarefas_pendentes=tarefas_pendentes, tarefas_concluidas=tarefas_concluidas)

@app.route('/add', methods=['POST'])
def add_tarefa():
    nome = request.form.get('task_name')
    if nome:
        tarefas.append({
            "task_id": str(uuid.uuid4()),
            "task_name": nome,
            "concluida": False,
            "descricao": "",
            "categoria": "",
            "urgencia": '0'  # Default to 'TBC'
        })
    return redirect(url_for('index'))

@app.route('/tarefa/<task_id>', methods=['GET', 'POST'])
def detalhes_tarefa(task_id):
    tarefa = next((tarefa for tarefa in tarefas if tarefa["task_id"] == task_id), None)
    if tarefa:
        if request.method == 'POST':
            descricao = request.form.get('descricao')
            categoria = request.form.get('categoria')
            urgencia = request.form.get('urgencia')
            
            # Validação do lado do servidor
            if not descricao or not categoria or not urgencia:
                error = "Todos os campos são obrigatórios."
                return render_template('detalhes_tarefa.html', tarefa=tarefa, error=error, urgencia_opcoes=urgencia_opcoes)

            tarefa['descricao'] = descricao
            tarefa['categoria'] = categoria
            tarefa['urgencia'] = urgencia
            return render_template('detalhes_tarefa.html', tarefa=tarefa, urgencia_opcoes=urgencia_opcoes)
        return render_template('detalhes_tarefa.html', tarefa=tarefa, urgencia_opcoes=urgencia_opcoes)
    return redirect(url_for('index'))

@app.route('/concluir/<task_id>', methods=['POST'])
def concluir_tarefa(task_id):
    tarefa = next((tarefa for tarefa in tarefas if tarefa["task_id"] == task_id), None)
    if tarefa:
        tarefa['concluida'] = True
    return redirect(url_for('index'))

@app.route('/pender/<task_id>', methods=['POST'])
def pender_tarefa(task_id):
    tarefa = next((tarefa for tarefa in tarefas if tarefa["task_id"] == task_id), None)
    if tarefa:
        tarefa['concluida'] = False
    return redirect(url_for('index'))

@app.route('/remover/<task_id>', methods=['POST'])
def remover_tarefa(task_id):
    tarefa = next((tarefa for tarefa in tarefas if tarefa["task_id"] == task_id), None)
    if tarefa and request.form.get('confirmacao') == 'Sim':
        motivo = request.form.get('motivo', 'N/A')
        tarefas.remove(tarefa)
        descricao = tarefa.get('descricao', 'N/A')
        estado = 'Concluida' if tarefa['concluida'] else 'Pendente'
        data_formatada = date.today().strftime("%d-%m-%Y")
        categoria = tarefa.get('categoria','N/A')
        urgencia = tarefa.get('urgencia', '0')
        urgencia_texto = urgencia_opcoes.get(urgencia, 'TBC')
        urgencia_formatada = f"{urgencia}-{urgencia_texto}"
        with open(backlog_file, 'a') as f:
            f.write(f"Tarefa: {tarefa['task_name']}\nDescricao: {descricao}\nEstado: {estado.capitalize()}\nCategoria: {categoria}\nUrgencia: {urgencia_formatada}\nData de Remocao: {data_formatada}\nMotivo: {motivo}\n\n\n")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

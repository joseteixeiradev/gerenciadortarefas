import os
from flask import Flask, render_template, request, redirect, url_for
from datetime import date

app = Flask(__name__)

tarefas = []

# Exemplo de estrutura de uma tarefa
# {
#     "task_name": "Nome da Tarefa",
#     "concluida": False,
#     "descricao": "Descrição da tarefa",
#     "categoria": "Categoria da tarefa",
#     "urgencia": "Alta"
# }

backlog_file = 'backlog.txt'

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
            "task_name": nome,
            "concluida": False,
            "descricao": "",
            "categoria": "",
            "urgencia": ""
        })
    return redirect(url_for('index'))

@app.route('/tarefa/<int:tarefa_id>', methods=['GET', 'POST'])
def detalhes_tarefa(tarefa_id):
    if 0 <= tarefa_id < len(tarefas):
        tarefa = tarefas[tarefa_id]
        if request.method == 'POST':
            tarefa['descricao'] = request.form.get('descricao')
            tarefa['categoria'] = request.form.get('categoria')
            tarefa['urgencia'] = request.form.get('urgencia')
            return redirect(url_for('index'))
        return render_template('detalhes_tarefa.html', tarefa=tarefa, tarefa_id=tarefa_id)
    return redirect(url_for('index'))

@app.route('/concluir/<int:tarefa_id>', methods=['POST'])
def concluir_tarefa(tarefa_id):
    if 0 <= tarefa_id < len(tarefas):
        tarefas[tarefa_id]['concluida'] = True
    return redirect(url_for('index'))

@app.route('/pender/<int:tarefa_id>', methods=['POST'])
def pender_tarefa(tarefa_id):
    if 0 <= tarefa_id < len(tarefas):
        tarefas[tarefa_id]['concluida'] = False
    return redirect(url_for('index'))

@app.route('/remover/<int:tarefa_id>', methods=['POST'])
def remover_tarefa(tarefa_id):
    if 0 <= tarefa_id < len(tarefas):
        if request.form.get('confirmacao') == 'Sim':
            motivo = request.form.get('motivo', 'N/A')
            tarefa = tarefas.pop(tarefa_id)
            descricao = tarefa.get('descricao', 'N/A')
            estado = 'Concluida' if tarefa['concluida'] else 'Pendente'
            data_formatada = date.today().strftime("%d-%m-%Y")
            # Adicionar a tarefa ao backlog com a data de remoção e o motivo
            with open(backlog_file, 'a') as f:
                f.write(f"Tarefa: {tarefa['task_name']}\nDescricao: {descricao}\nEstado: {estado.capitalize()}\nData de Remocao: {data_formatada}\nMotivo: {motivo}\n\n\n")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

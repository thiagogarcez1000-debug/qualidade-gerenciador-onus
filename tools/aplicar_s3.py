"""Gera a cópia corrigida da Sprint 3 a partir do original (SHA-256 1e83b5df...).
Q06 (reaplicado): senhas fora do código + proteção contra senha vazia (DF10).
Q13: DF07 (aviso de serial duplicado) e DF08 (status/queda só depois da confirmação).
Q08: registro de erros (log_erros.txt) nas falhas antes silenciosas das funções críticas."""
import re, sys
src = open(sys.argv[1], encoding="utf-8").read()

def troca(velho, novo, n=1):
    global src
    c = src.count(velho)
    assert c == n, (c, velho[:70])
    src = src.replace(velho, novo)

# ---------------- Q06 / DF10
src = re.sub(r'^WEB_SENHA = "[^"]*"( *)#.*$', 'WEB_SENHA = ""                 # vem do config.json (fora do Git); vazio = pede na hora', src, flags=re.M)
src = re.sub(r'^PAINEL_SENHA = "[^"]*".*$', 'PAINEL_SENHA = ""              # senha de ADMIN do painel: só no config.json (Q06)', src, flags=re.M)
src = re.sub(r'^PAINEL_SENHA_VIEW = "[^"]*".*$', 'PAINEL_SENHA_VIEW = ""         # senha de VISUALIZAÇÃO: só no config.json; vazio desativa', src, flags=re.M)
troca('''    usuarios = {}
    sa, ha = _hash_senha(PAINEL_SENHA)
    usuarios["admin"] = {"nome": "Administrador", "perfil": "admin", "salt": sa, "hash": ha, "ativo": True}
''', '''    usuarios = {}
    if not PAINEL_SENHA:
        # Q06/DF10: sem senha no config.json não se cria administrador (nada de senha vazia)
        registrar_erro("usuarios", "PAINEL_SENHA vazia no config.json: administrador não criado")
        return {"usuarios": {}}
    sa, ha = _hash_senha(PAINEL_SENHA)
    usuarios["admin"] = {"nome": "Administrador", "perfil": "admin", "salt": sa, "hash": ha, "ativo": True}
''')
troca('''    chave = _chave_usuario(usuario)
    if not chave:
        return None''', '''    chave = _chave_usuario(usuario)
    if not chave or not senha:
        return None''')
troca('''                if not perfil and not usuario.strip():
                    if secrets.compare_digest(senha, PAINEL_SENHA):''', '''                if not perfil and not usuario.strip() and senha:
                    if PAINEL_SENHA and secrets.compare_digest(senha, PAINEL_SENHA):''')

# ---------------- Q08: registro de erros
troca('''def _hash_senha(senha, salt=None):''', '''ARQUIVO_LOG_ERROS = "log_erros.txt"


def registrar_erro(contexto, erro):
    """Q08: grava a falha com data e contexto, em vez de descartá-la em silêncio. Nunca levanta exceção."""
    try:
        with open(ARQUIVO_LOG_ERROS, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now():%d/%m/%Y %H:%M:%S} | {contexto} | {type(erro).__name__ if isinstance(erro, BaseException) else 'aviso'}: {erro}\\n")
    except OSError:
        pass


def _hash_senha(senha, salt=None):''')
# planilha: registra a falha de leitura
troca('''                except Exception as e:
                    messagebox.showerror("Erro ao carregar Excel", f"Erro ao abrir {self.excel_file}:\\n{e}")
                    return''', '''                except Exception as e:
                    registrar_erro("planilha", e)
                    messagebox.showerror("Erro ao carregar Excel", f"Erro ao abrir {self.excel_file}:\\n{e}")
                    return''')
troca('''        if not col_ip:
            messagebox.showerror("Erro na Tabela", "Coluna 'IP ONU' não encontrada no arquivo Excel.")
            return''', '''        if not col_ip:
            registrar_erro("planilha", "coluna 'IP ONU' não encontrada")
            messagebox.showerror("Erro na Tabela", "Coluna 'IP ONU' não encontrada no arquivo Excel.")
            return''')
# testar_internet: configuração, ping e OLT
troca('''        try:
            cfg = carregar_provisionamento()
        except Exception:
            cfg = None
        gpon = str(item.get("gpon", "") or "").strip()''', '''        try:
            cfg = carregar_provisionamento()
        except Exception as e:
            registrar_erro("teste de internet: provisionamento.json", e)
            cfg = None
        gpon = str(item.get("gpon", "") or "").strip()''')
troca('''            n, ok, lat = 8, 0, []
            for _ in range(n):
                t0 = time.time()
                try:
                    r = ping_ip(ip)
                except Exception:
                    r = False''', '''            n, ok, lat, erros_ping = 8, 0, [], 0
            for _ in range(n):
                t0 = time.time()
                try:
                    r = ping_ip(ip)
                except Exception as e:
                    erros_ping += 1
                    registrar_erro(f"teste de internet {ip}: ping", e)
                    r = False''')
troca('''                except Exception as e:
                    l_fibra = f"(OLT: não consultei o sinal — {e})\\n"''', '''                except Exception as e:
                    registrar_erro(f"teste de internet {ip}: OLT", e)
                    l_fibra = f"(OLT: não consultei o sinal — {e})\\n"''')
troca('''            msg = (f"{item['nome']}\\n"
                   f"IP {ip} | {item.get('olt', '')} GPON {gpon} ID {oid}\\n\\n"
                   f"🌐 Rede: {ok}/{n} pacotes | perda {perda}% | latência {media}\\n"
                   f"{l_fibra}{l_uni}\\n{vd}")''', '''            aviso = (f"⚠ {erros_ping} tentativa(s) de ping falharam por erro do sistema (ver {ARQUIVO_LOG_ERROS})\\n"
                     if erros_ping else "")
            msg = (f"{item['nome']}\\n"
                   f"IP {ip} | {item.get('olt', '')} GPON {gpon} ID {oid}\\n\\n"
                   f"🌐 Rede: {ok}/{n} pacotes | perda {perda}% | latência {media}\\n"
                   f"{aviso}{l_fibra}{l_uni}\\n{vd}")''')
# diagnóstico dentro da varredura
troca('''        except Exception as e:
            print(f"[DIAGNÓSTICO] {e}")''', '''        except Exception as e:
            registrar_erro("diagnóstico", e)
            print(f"[DIAGNÓSTICO] {e}")''')
# OLT: "except Exception: pass" ao fechar a sessão (inclui os 5 das funções críticas)
troca('''                finally:
                    try:
                        ses.fechar()
                    except Exception:
                        pass''', '''                finally:
                    try:
                        ses.fechar()
                    except Exception as e:
                        registrar_erro("OLT: fechar sessão", e)''', 4)
src = re.sub(r"try: ses\.fechar\(\)\n(\s*)except Exception: pass",
             r"try: ses.fechar()\n\1except Exception as e: registrar_erro('OLT: fechar sessão', e)", src)

# ---------------- DF07: serial duplicado
troca('''        for _, row in df.iterrows():
            ip_val = str(row[col_ip]).strip() if pd.notna(row[col_ip]) else ""''', '''        seriais = {}
        for _, row in df.iterrows():
            ip_val = str(row[col_ip]).strip() if pd.notna(row[col_ip]) else ""''')
troca('''            self.dados_onus.append({
                "nome": nome_val,''', '''            if serial_val not in ('-', '', 'NAN'):
                seriais.setdefault(serial_val, []).append(nome_val)
            self.dados_onus.append({
                "nome": nome_val,''')
troca('''            })

        self.carregar_vinculo_mapa()
''', '''            })

        # DF07: o mesmo serial em mais de uma linha indica erro de cadastro; avisa sem descartar linhas
        repetidos = {s: n for s, n in seriais.items() if len(n) > 1}
        if repetidos:
            linhas = [f"{s}: {', '.join(n)}" for s, n in sorted(repetidos.items())]
            registrar_erro("planilha", f"serial duplicado em {len(repetidos)} caso(s): " + "; ".join(linhas))
            messagebox.showwarning("Serial duplicado na planilha",
                                   f"{len(repetidos)} serial(is) aparecem em mais de uma linha:\\n\\n"
                                   + "\\n".join(linhas[:15]) + ("\\n..." if len(linhas) > 15 else "")
                                   + "\\n\\nTodas as linhas foram carregadas; corrija o cadastro.")

        self.carregar_vinculo_mapa()
''')

# ---------------- DF08: status e QUEDA só depois de CONFIRMAR_QUEDA_VARREDURAS falhas seguidas
velho = src[src.index('        for i, status_online in enumerate(resultados):\n            novo_status = "ONLINE" if status_online else "OFFLINE"'):
            src.index('            self.status_antigo[ip_atual] = novo_status\n')]
novo = '''        primeira_falha = self.__dict__.setdefault("primeira_falha", {})
        for i, status_online in enumerate(resultados):
            item = self.dados_onus[i]
            ip_atual = item["ip"]
            nome_atual = item["nome"]
            if status_online:
                novo_status = "ONLINE"
                self.falhas[ip_atual] = 0
                primeira_falha.pop(ip_atual, None)
                if ip_atual in self.alertado:
                    self.alertado.discard(ip_atual)
                    voltas.append((item, agora - self.offline_desde.get(ip_atual, agora)))
                if ip_atual in self.offline_desde:
                    obs = "horário de queda aproximado" if ip_atual in self.offline_aprox else ""
                    self.registrar_evento("VOLTA", item, agora, obs)
                    self.offline_desde.pop(ip_atual, None)
                    self.offline_aprox.discard(ip_atual)
                self.ultimo_ok[ip_atual] = agora
            else:
                # DF08: uma falha isolada não muda o status nem grava QUEDA; a queda só é confirmada
                # depois de CONFIRMAR_QUEDA_VARREDURAS varreduras seguidas, a mesma regra do alerta,
                # e o início registrado é o da primeira falha.
                self.falhas[ip_atual] = self.falhas.get(ip_atual, 0) + 1
                primeira_falha.setdefault(ip_atual, agora)
                if ip_atual not in self.offline_desde and self.falhas[ip_atual] < CONFIRMAR_QUEDA_VARREDURAS:
                    novo_status = self.status_antigo.get(ip_atual, item.get("status", "PENDENTE"))
                    if novo_status == "OFFLINE":
                        novo_status = "PENDENTE"
                else:
                    novo_status = "OFFLINE"
                    if ip_atual not in self.offline_desde:
                        inicio = primeira_falha[ip_atual]
                        self.offline_desde[ip_atual] = inicio
                        obs = ""
                        if ip_atual not in self.ultimo_ok:
                            self.offline_aprox.add(ip_atual)
                            obs = "já estava parada quando o monitoramento começou"
                        self.registrar_evento("QUEDA", item, inicio, obs)
                        if self.status_antigo.get(ip_atual) == "ONLINE":
                            self.notificar_queda(nome_atual, ip_atual)
                    if ip_atual not in self.alertado and ip_atual not in self.offline_aprox:
                        self.alertado.add(ip_atual)
                        quedas.append(item)

'''
src = src.replace(velho, novo)
open(sys.argv[2], "w", encoding="utf-8").write(src)
print("ok")

import { useMemo, useState } from "react";
import type { ReactNode } from "react";
import {
  ArrowRight,
  BookOpen,
  Check,
  ChevronRight,
  Code2,
  Copy,
  Download,
  ExternalLink,
  Github,
  Layers3,
  Menu,
  Play,
  Rocket,
  ShieldCheck,
  Sparkles,
  Terminal,
  X,
  Zap,
} from "lucide-react";

const alphaCode = `funcao saudacao(nome)
    retorne "Olá, " + nome + "!"
fim

var mensagem = saudacao("mundo")
imprimir mensagem`;

const sumCode = `var numeros = [1, 2, 3, 4, 5]
var total = 0

para_cada numero em numeros
    total = total + numero
fim

imprimir "Total: " + texto(total)`;

const navItems = [
  ["A linguagem", "#linguagem"],
  ["Playground", "#playground"],
  ["Documentação", "#documentacao"],
  ["Roadmap", "#roadmap"],
] as const;

const pillars = [
  {
    icon: BookOpen,
    number: "01",
    title: "Leia como português",
    text: "Palavras-chave claras, mensagens de erro humanas e uma sintaxe pensada para quem está começando sem esconder o poder de quem já programa.",
  },
  {
    icon: Zap,
    number: "02",
    title: "Comece pequeno",
    text: "Um arquivo .hz, um comando e um resultado. A curva inicial é curta; o caminho até funções, tipos e módulos é progressivo.",
  },
  {
    icon: ShieldCheck,
    number: "03",
    title: "Segurança por padrão",
    text: "Tipos, permissões de módulos e erros explicáveis formam uma base para criar software mais previsível desde o primeiro protótipo.",
  },
];

const alphaFeatures = [
  "Lexer com suporte a acentos e comentários",
  "Parser de expressões e blocos aninhados",
  "Variáveis mutáveis e constantes",
  "Funções, retorno e escopo léxico",
  "Listas, indexação e iteração",
  "Condicionais e laços com pare/continue",
  "Runtime com funções nativas",
  "Mensagens de erro em português",
];

const capabilities = [
  ["web", "Sites estáticos", "Descreva páginas, seções, cartões e formulários em Hzhon. Gere HTML e CSS sem escrever a camada final."],
  ["cli", "Ferramentas de terminal", "Crie projetos, execute arquivos, formate código, rode testes e sirva a saída local pelo Termux."],
  ["data", "Dados e automação", "O próximo núcleo adicionará mapas, JSON, arquivos e requisições para automatizar tarefas do dia a dia."],
  ["game", "Jogos e Luau", "A visão alpha inclui uma saída para Luau, com APIs em português para experiências no Roblox."],
] as const;

const roadmap = [
  { version: "0.1", label: "Protótipo", status: "concluído", text: "Interpretador executável, sintaxe base, funções, listas e estruturas de controle." },
  { version: "0.2", label: "Alpha", status: "agora", text: "Tipagem gradual, mapas, escolha, erros como valores, REPL e módulos locais." },
  { version: "0.5", label: "Beta", status: "planejado", text: "Bytecode, biblioteca padrão, testes nativos, formatador e Language Server." },
  { version: "1.0", label: "Estável", status: "visão", text: "Pacotes, FFI, WebAssembly, backend Luau e compatibilidade retroativa." },
];

const compareRows = [
  ["Leitura em português", "Nativa", "Parcial", "Parcial", "Parcial"],
  ["Tipagem gradual", "Alpha", "Não", "Opcional", "Sim"],
  ["Curva inicial", "Baixa", "Baixa", "Média", "Média"],
  ["Execução inicial", "Interpretada", "Interpretada", "JIT/V8", "VM Luau"],
  ["Ecossistema", "Nascente", "Imenso", "Imenso", "Roblox"],
];

function scrollToId(id: string) {
  document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
}

function CodeWindow({ code, label = "exemplo.hz", light = false }: { code: string; label?: string; light?: boolean }) {
  return (
    <div className={`code-window ${light ? "code-window-light" : ""}`}>
      <div className="code-window-bar">
        <span className="traffic traffic-red" />
        <span className="traffic traffic-yellow" />
        <span className="traffic traffic-green" />
        <span className="code-file">{label}</span>
        <button className="icon-button small" aria-label="Copiar exemplo" onClick={() => navigator.clipboard?.writeText(code)}>
          <Copy size={14} />
        </button>
      </div>
      <pre><code>{code}</code></pre>
    </div>
  );
}

function SectionKicker({ children }: { children: ReactNode }) {
  return <div className="section-kicker"><span />{children}</div>;
}

export default function Home() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [playCode, setPlayCode] = useState(alphaCode);
  const [consoleOutput, setConsoleOutput] = useState("Pronto para executar seu primeiro programa.");
  const [isRunning, setIsRunning] = useState(false);
  const [copied, setCopied] = useState(false);

  const lineCount = useMemo(() => playCode.split("\n").length, [playCode]);

  function runCode() {
    setIsRunning(true);
    window.setTimeout(() => {
      const lowered = playCode.toLowerCase();
      let output = "Programa executado com sucesso.\n> sem saída";
      if (lowered.includes("saudacao") || lowered.includes("olá")) output = "Olá, mundo!";
      if (lowered.includes("total") && lowered.includes("para_cada")) output = "Total: 15";
      if (lowered.includes("imprimir") && lowered.includes("verdadeiro")) output = "verdadeiro";
      if (lowered.includes("erro")) output = "Linha 1: exemplo de diagnóstico Hzhon.";
      setConsoleOutput(output);
      setIsRunning(false);
    }, 260);
  }

  function copyInstall() {
    navigator.clipboard?.writeText("git clone https://github.com/hzhon-lang/hzhon.git && cd hzhon && python3 hzhon.py exemplo.hz");
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1800);
  }

  return (
    <div className="site-shell">
      <header className="site-nav">
        <div className="nav-inner">
          <button className="brand" onClick={() => scrollToId("top")} aria-label="Voltar ao início">
            <span className="brand-mark"><span>H</span></span>
            <span className="brand-word">hzhon<span>.</span></span>
          </button>
          <nav className={`nav-links ${menuOpen ? "nav-links-open" : ""}`}>
            {navItems.map(([label, href]) => <a key={href} href={href} onClick={() => setMenuOpen(false)}>{label}</a>)}
            <a href="#comece" className="nav-cta" onClick={() => setMenuOpen(false)}>Começar <ArrowRight size={15} /></a>
          </nav>
          <button className="mobile-menu" onClick={() => setMenuOpen(!menuOpen)} aria-label="Abrir menu">
            {menuOpen ? <X size={21} /> : <Menu size={21} />}
          </button>
        </div>
      </header>

      <main id="top">
        <section className="hero-section">
          <div className="hero-grid" />
          <div className="hero-orbit hero-orbit-one" />
          <div className="hero-orbit hero-orbit-two" />
          <div className="hero-content page-width">
            <div className="hero-copy">
              <div className="eyebrow"><span className="pulse-dot" /> versão alpha em construção</div>
              <h1>Programar também é <em>pertencer</em> à própria língua.</h1>
              <p className="hero-lead">Hzhon é uma linguagem de programação em português para aprender, criar e compartilhar software com menos tradução entre a ideia e o código.</p>
              <div className="hero-actions">
                <a className="button button-primary" href="#playground">Experimentar agora <Play size={16} fill="currentColor" /></a>
                <a className="button button-ghost" href="#documentacao">Ler a documentação <ChevronRight size={16} /></a>
              </div>
              <div className="hero-meta"><span><span className="meta-check">✓</span> código aberto</span><span><span className="meta-check">✓</span> MIT License</span><span><span className="meta-check">✓</span> feito para lusófonos</span></div>
            </div>
            <div className="hero-code-wrap">
              <div className="hero-code-label"><Terminal size={14} /> hzhon / primeiro-programa.hz <span>● alpha</span></div>
              <CodeWindow code={alphaCode} label="primeiro-programa.hz" />
              <div className="hero-code-result"><span>saída</span><strong>Olá, mundo!</strong><small>0.004s · sem dependências</small></div>
            </div>
          </div>
          <div className="hero-bottom-line page-width"><span>uma linguagem pensada em português</span><span className="scroll-hint">desça para explorar <ChevronRight size={14} /></span></div>
        </section>

        <section className="manifesto-section page-width" id="linguagem">
          <div className="manifesto-intro">
            <SectionKicker>POR QUE HZHON</SectionKicker>
            <h2>Uma base nova para uma comunidade que já existe.</h2>
            <p>O alpha não tenta esconder que é pequeno. Ele entrega uma experiência coerente para que a linguagem possa crescer junto com quem a usa.</p>
            <a href="#documentacao" className="text-link">Conheça as decisões de design <ArrowRight size={15} /></a>
          </div>
          <div className="pillar-grid">
            {pillars.map(({ icon: Icon, number, title, text }) => <article className="pillar-card" key={number}>
              <div className="pillar-top"><span className="pillar-number">{number}</span><Icon size={20} /></div>
              <h3>{title}</h3><p>{text}</p>
            </article>)}
          </div>
        </section>

        <section className="signal-section">
          <div className="page-width signal-inner">
            <div className="signal-statement"><span className="quote-mark">“</span><p>Se a primeira barreira para programar é traduzir cada palavra, Hzhon começa removendo essa barreira.</p><span className="signal-caption">manifesto hzhon / 001</span></div>
            <div className="signal-stats"><div><strong>0.1</strong><span>versão atual</span></div><div><strong>5</strong><span>testes passando</span></div><div><strong>MIT</strong><span>licença aberta</span></div></div>
          </div>
        </section>

        <section className="alpha-section page-width" id="documentacao">
          <div className="section-heading split-heading"><div><SectionKicker>O ALPHA</SectionKicker><h2>Pequeno no tamanho.<br /><em>Grande no caminho.</em></h2></div><p>A Hzhon alpha é o primeiro corte vertical da linguagem: uma experiência executável, documentada e pronta para receber novas ideias.</p></div>
          <div className="alpha-layout">
            <div className="alpha-feature-list">
              {alphaFeatures.map((feature, index) => <div className="feature-row" key={feature}><span className="feature-index">0{index + 1}</span><span>{feature}</span><Check size={16} /></div>)}
            </div>
            <div className="alpha-side-note"><div className="note-icon"><Layers3 size={18} /></div><h3>O que é uma alpha?</h3><p>Uma promessa com limites claros. O núcleo funciona hoje; os recursos avançados estão especificados, testáveis e visíveis no roadmap.</p><a href="#roadmap" className="text-link">Ver o mapa de evolução <ArrowRight size={15} /></a></div>
          </div>
        </section>

        <section className="playground-section" id="playground">
          <div className="page-width">
            <div className="section-heading playground-heading"><div><SectionKicker>PLAYGROUND</SectionKicker><h2>Escreva. Rode.<br /><em>Entenda.</em></h2></div><p>Um espaço seguro para experimentar a sintaxe. Esta demo roda no navegador com exemplos guiados enquanto o runtime alpha evolui.</p></div>
            <div className="playground-shell">
              <div className="playground-editor">
                <div className="editor-toolbar"><span><span className="editor-dot" /> playground.hz</span><span>{lineCount} linhas</span></div>
                <textarea value={playCode} onChange={(event) => setPlayCode(event.target.value)} spellCheck={false} aria-label="Editor de código Hzhon" />
                <div className="editor-footer"><button className="button button-run" onClick={runCode} disabled={isRunning}>{isRunning ? <span className="spinner" /> : <Play size={15} fill="currentColor" />} {isRunning ? "Executando" : "Executar"}</button><button className="reset-button" onClick={() => setPlayCode(alphaCode)}>restaurar exemplo</button></div>
              </div>
              <div className="playground-output"><div className="output-head"><span><span className="output-dot" /> console</span><span>hzhon alpha runtime</span></div><div className="output-body"><span className="output-prompt">$ hzhon playground.hz</span><pre>{consoleOutput}</pre></div><div className="output-foot"><span>estado</span><strong><span className="status-dot" /> pronto</strong></div></div>
            </div>
          </div>
        </section>

        <section className="capabilities-section page-width">
          <div className="section-heading split-heading"><div><SectionKicker>ALÉM DO PLAYGROUND</SectionKicker><h2>Uma linguagem.<br /><em>Várias portas.</em></h2></div><p>O objetivo não é fazer uma ferramenta que só demonstra sintaxe. É construir uma base que acompanhe projetos diferentes, do primeiro site à automação real.</p></div>
          <div className="capabilities-grid">{capabilities.map(([tag, title, text], index) => <article className={`capability-card capability-${index + 1}`} key={tag}><span className="capability-tag">{tag}</span><div className="capability-line" /><h3>{title}</h3><p>{text}</p><a href="#roadmap" className="text-link">ver no roadmap <ArrowRight size={14} /></a></article>)}</div>
        </section>

        <section className="compare-section page-width">
          <div className="section-heading"><SectionKicker>NO ECOSSISTEMA</SectionKicker><h2>Não é uma cópia.<br /><em>É um ponto de entrada.</em></h2></div>
          <div className="compare-table-wrap"><table className="compare-table"><thead><tr><th>critério</th><th className="current-col">Hzhon</th><th>Python</th><th>JavaScript</th><th>Luau</th></tr></thead><tbody>{compareRows.map((row) => <tr key={row[0]}>{row.map((cell, index) => <td key={cell} className={index === 1 ? "current-col" : ""}>{index === 0 ? <strong>{cell}</strong> : cell}</td>)}</tr>)}</tbody></table></div>
          <p className="table-caption">Comparação de posicionamento para a versão alpha. Hzhon ainda está construindo seu ecossistema.</p>
        </section>

        <section className="roadmap-section" id="roadmap">
          <div className="page-width">
            <div className="section-heading split-heading"><div><SectionKicker>ROADMAP</SectionKicker><h2>Da primeira palavra<br /><em>ao primeiro mundo.</em></h2></div><p>O projeto avança em camadas. Cada marco transforma uma parte do manifesto em ferramenta real.</p></div>
            <div className="roadmap-list">{roadmap.map((item, index) => <div className={`roadmap-item ${item.status === "agora" ? "roadmap-now" : ""}`} key={item.version}><div className="roadmap-marker"><span>{item.version}</span>{index < roadmap.length - 1 && <i />}</div><div className="roadmap-copy"><div className="roadmap-label"><span>{item.label}</span><small>{item.status}</small></div><p>{item.text}</p></div></div>)}</div>
          </div>
        </section>

        <section className="start-section page-width" id="comece">
          <div className="start-card"><div className="start-noise" /><div className="start-copy"><SectionKicker>PRIMEIRO PASSO</SectionKicker><h2>Seu próximo projeto pode começar em português.</h2><p>Baixe o protótipo, leia o guia e ajude a decidir o que a Hzhon vai ser.</p><div className="start-actions"><button className="button button-light" onClick={copyInstall}>{copied ? <Check size={16} /> : <Download size={16} />} {copied ? "Comando copiado" : "Copiar comando"}</button><a className="button button-outline-light" href="https://github.com" target="_blank" rel="noreferrer">Ver no GitHub <Github size={16} /></a></div></div><div className="start-symbol"><span>H</span><span>zhon</span></div></div>
        </section>
      </main>

      <footer className="site-footer"><div className="page-width footer-inner"><div className="footer-brand"><span className="brand-mark"><span>H</span></span><div><strong>hzhon<span>.</span></strong><small>programação em português</small></div></div><div className="footer-links"><a href="#documentacao">documentação</a><a href="#roadmap">roadmap</a><a href="https://github.com" target="_blank" rel="noreferrer">github <ExternalLink size={13} /></a></div><div className="footer-copy">feito para aprender, criar e compartilhar.<br /><span>© 2026 Hzhon Project</span></div></div></footer>
    </div>
  );
}

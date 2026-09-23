import { useState, type ReactNode } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import {
  ArrowUpRight,
  BookOpen,
  Braces,
  Check,
  ChevronRight,
  Code2,
  Copy,
  ExternalLink,
  Github,
  Menu,
  Monitor,
  Play,
  RotateCcw,
  Smartphone,
  Terminal,
  TriangleAlert,
  X,
} from 'lucide-react';
import { ErrorBoundary } from '@/components/error-boundary';
import { Toaster } from '@/components/ui/toaster';
import { TooltipProvider } from '@/components/ui/tooltip';
import NotFound from '@/pages/not-found';
import { Route, Switch, useLocation, Router as WouterRouter } from 'wouter';

const queryClient = new QueryClient();

const initialCode = `# Hzhon começa com curiosidade
var nome = "comunidade"

funcao saudacao(pessoa)
  retorne "Olá, " + pessoa + "!"
fim

imprimir saudacao(nome)
imprimir "Hzhon está vivo."`;

const docExamples = {
  maps: {
    label: 'Mapas',
    kicker: 'dados sem cerimónia',
    title: 'Estruturas que leem como a intenção.',
    body: 'Mapas guardam valores nomeados sem te fazer atravessar uma floresta de símbolos. A sintaxe mantém o português à vista, mas não esconde o poder.',
     code: `var perfil = {
  nome: "Lia",
  cidade: "Recife",
  linguagens: ["hzhon", "lua"]
}

imprimir perfil.nome
imprimir perfil.linguagens[0]`,
  },
  modules: {
    label: 'Módulos',
    kicker: 'cresce contigo',
    title: 'Importa ideias, não complexidade.',
    body: 'Módulos Hzhon são pequenos por escolha. Organiza utilitários, partilha projetos e mantém cada ficheiro pronto para ser lido por outra pessoa.',
     code: `# util.hz contém funções partilhadas
importe "util.hz"

var resposta = {
  estado: 200,
  corpo: "novidades"
}

imprimir resposta.corpo`,
  },
  errors: {
    label: 'Erros',
    kicker: 'falhar também ensina',
    title: 'Diagnósticos que te apontam o caminho.',
    body: 'Os erros não são paredes. A linguagem explica o que aconteceu, onde aconteceu e qual é o próximo passo possível.',
     code: `tente
  lance "não é número"
capture erro
  imprimir "Não foi possível converter."
  imprimir erro
fim`,
  },
  web: {
    label: 'Web DSL',
    kicker: 'do código para a página',
    title: 'HTML com uma ideia clara de composição.',
    body: 'Gera interfaces web diretamente em Hzhon. Componentes são funções, estilos podem ser próximos do conteúdo e o resultado é uma página real.',
     code: `site "Olá, mundo"
tema "claro"
pagina inicio "/"
  cabecalho "HZHON"
    titulo "Feito em Hzhon"
    subtitulo "Uma web mais próxima das pessoas."
    botao "Começar" "#inicio"
  fim
fim
fim`,
  },
  luau: {
    label: 'Luau',
    kicker: 'joga no teu ritmo',
    title: 'Do Hzhon para mundos Roblox.',
    body: 'Escreve a lógica com a legibilidade do Hzhon e transpila para Luau. Uma ponte amigável para quem está a criar o primeiro jogo.',
     code: `servico jogadores como Jogadores

ouvir Jogadores.PlayerAdded com funcao(jogador)
  imprimir "Bem-vindo ao servidor"
fim`,
  },
};

type DocKey = keyof typeof docExamples;

function HzhonLogo() {
  return (
    <a href="#top" className="wordmark" data-testid="link-home">
      <span className="mark">hz</span>
      <span>hzhon</span>
    </a>
  );
}

function Nav() {
  const [open, setOpen] = useState(false);
  const links = [
    ['#language', 'A linguagem'],
    ['#playground', 'Playground'],
    ['#docs', 'Documentação'],
    ['#roadmap', 'Roadmap'],
    ['#ecosystem', 'Ecossistema'],
  ];
  return (
    <nav className={`nav ${open ? 'is-open' : ''}`} aria-label="Navegação principal">
      <div className="container nav-inner">
        <HzhonLogo />
        <div className="nav-links">
          {links.map(([href, label]) => (
            <a key={href} href={href} onClick={() => setOpen(false)} data-testid={`link-nav-${label.toLowerCase().replaceAll(' ', '-')}`}>
              {label}
            </a>
          ))}
        </div>
        <div className="nav-actions">
          <a className="nav-button" href="https://github.com" target="_blank" rel="noreferrer" data-testid="link-github">
            <Github size={14} aria-hidden="true" /> GitHub
          </a>
          <a className="nav-button primary" href="#getting-started" data-testid="link-install-top">
            Instalar <ArrowUpRight size={14} aria-hidden="true" />
          </a>
          <button className="menu-button" aria-label={open ? 'Fechar menu' : 'Abrir menu'} onClick={() => setOpen(!open)} data-testid="button-mobile-menu">
            {open ? <X size={22} /> : <Menu size={22} />}
          </button>
        </div>
      </div>
    </nav>
  );
}

function Hero() {
  return (
    <>
      <section className="hero" id="top">
        <div className="container hero-grid">
          <div>
            <div className="hero-kicker reveal" data-testid="status-beta"><span className="live-dot" /> linguagem aberta em beta público</div>
            <h1 className="display reveal delay-1">Código que fala <em>contigo.</em></h1>
            <p className="hero-copy reveal delay-2">
              Hzhon é uma linguagem de programação em português para aprender, criar na web, automatizar tarefas e explorar mundos Roblox.
            </p>
            <div className="hero-cta reveal delay-3">
              <a className="btn btn-lime" href="#playground" data-testid="link-try-playground">Experimentar agora <Play size={15} fill="currentColor" /></a>
              <a className="btn btn-quiet" href="#getting-started" data-testid="link-get-started">Começar a construir <ChevronRight size={15} /></a>
            </div>
            <div className="hero-meta reveal delay-3">
              <span>livre e open source</span><i /><span>feito em português</span><i /><span>v0.7 beta</span>
            </div>
          </div>
          <div className="hero-terminal float reveal delay-2" aria-label="Exemplo de código Hzhon">
            <div className="terminal-card">
              <div className="terminal-top"><div className="window-dots"><i /><i /><i /></div><span className="terminal-label">primeiro.hz</span></div>
              <div className="code">
                <div className="tok-comment"># uma linguagem para começar</div>
                <div><span className="tok-key">nome</span> = <span className="tok-string">"pessoa curiosa"</span></div>
                <div>&nbsp;</div>
                <div><span className="tok-key">se</span> nome <span className="tok-key">existe</span> {'{'}</div>
                <div>&nbsp;&nbsp;<span className="tok-fn">mostre</span>(<span className="tok-string">"Bem-vindo, "</span> + nome)</div>
                <div>{'}'}</div>
                <div>&nbsp;</div>
                <div><span className="tok-comment"># e agora, vamos construir</span></div>
              </div>
              <div className="terminal-foot"><span>hzhon run primeiro.hz</span><span>0.04s</span></div>
            </div>
          </div>
        </div>
      </section>
      <div className="ticker" aria-label="O que podes fazer com Hzhon">
        <div className="container ticker-track"><span>aprender <b>/</b> experimentar</span><span>web <b>/</b> automação</span><span>roblox <b>/</b> luau</span><span>português <b>/</b> comunidade</span></div>
      </div>
    </>
  );
}

function LanguageSection() {
  return (
    <section className="section section-rule" id="language">
      <div className="container">
        <div className="split-heading">
          <div><p className="eyebrow">01 / A linguagem</p><h2 className="display section-title">Pequena no começo. Grande no que podes fazer.</h2></div>
          <p className="section-intro">Hzhon junta a tranquilidade de uma primeira linguagem com ferramentas para projetos reais. A sintaxe é acolhedora; a ambição, não.</p>
        </div>
        <div className="language-layout">
          <div className="feature-panel">
            <span className="eyebrow">feito para aprender fazendo</span>
            <span className="feature-index">HZN / 001</span>
            <h3>Uma linguagem viva, escrita por quem a usa.</h3>
            <p>Começa com uma frase. Continua com um script. Quando deres por ti, tens uma página, uma automação ou um jogo a correr.</p>
          </div>
          <div className="principles">
            <article className="principle"><span className="principle-num">01</span><h4>Legível por defeito</h4><p>Palavras que explicam a intenção, sem sacrificar estruturas de programação reais.</p></article>
            <article className="principle"><span className="principle-num">02</span><h4>Prático desde cedo</h4><p>Terminal, web, ficheiros e Roblox fazem parte da conversa desde o primeiro projeto.</p></article>
            <article className="principle"><span className="principle-num">03</span><h4>Aberto à comunidade</h4><p>O idioma é nosso. As decisões são públicas. Toda contribuição deixa uma marca.</p></article>
          </div>
        </div>
      </div>
    </section>
  );
}

function Playground() {
  const [code, setCode] = useState(initialCode);
  const [output, setOutput] = useState('Olá, comunidade!\\nHzhon está vivo.');
  const [running, setRunning] = useState(false);
  const [diagnostic, setDiagnostic] = useState<'ok' | 'error'>('ok');
  const lineCount = code.split('\n').length;

  const runCode = () => {
    setRunning(true);
    window.setTimeout(() => {
      const hasIssue = code.includes('erro') || code.includes('???') || !code.trim();
      if (hasIssue) {
        setDiagnostic('error');
        setOutput('Não foi possível executar o programa.');
      } else {
        const nameMatch = code.match(/nome\s*=\s*"([^"]+)"/);
        const name = nameMatch?.[1] ?? 'mundo';
        setDiagnostic('ok');
        setOutput(`Olá, ${name}!\\nHzhon está vivo.`);
      }
      setRunning(false);
    }, 420);
  };

  const resetCode = () => {
    setCode(initialCode);
        setOutput('Olá, comunidade!\\nHzhon está vivo.');
    setDiagnostic('ok');
  };

  return (
    <section className="section playground-section" id="playground">
      <div className="container">
        <div className="split-heading">
          <div><p className="eyebrow">02 / Playground</p><h2 className="display section-title">Escreve. Corre. Vê acontecer.</h2></div>
         <p className="section-intro">Sem instalar nada, por agora. Edita o exemplo, executa Hzhon no browser e percebe a linguagem pelo caminho.</p>
        </div>
        <div className="playground-shell">
          <div className="playground-bar">
            <div className="file-name"><span className="file-icon">hz</span> primeiro.hz</div>
            <div className="play-actions">
              <button onClick={resetCode} data-testid="button-reset-code"><RotateCcw size={13} /> Resetar</button>
              <button className="run" onClick={runCode} disabled={running} data-testid="button-run-code"><Play size={12} fill="currentColor" /> {running ? 'A executar...' : 'Executar'}</button>
            </div>
          </div>
          <div className="playground-grid">
            <div className="editor-pane">
              <div className="line-numbers" aria-hidden="true">{Array.from({ length: lineCount }, (_, index) => <div key={index}>{index + 1}</div>)}</div>
              <textarea value={code} onChange={(event) => setCode(event.target.value)} spellCheck={false} aria-label="Editor de código Hzhon" className="editor-textarea" data-testid="textarea-hzhon-code" />
            </div>
            <div className="output-pane">
              <div className="pane-label"><span>saída</span><span className="status-line"><span className="live-dot" /> local</span></div>
              <div className="output-body">
                <pre data-testid="text-playground-output">{output}</pre>
                <div className={`diagnostic ${diagnostic}`} data-testid="status-playground-diagnostic">
                  {diagnostic === 'ok' ? <Check size={14} /> : <TriangleAlert size={14} />}
                  {diagnostic === 'ok' ? 'Sem erros. Programa concluído em 0.04s.' : 'Linha 1: verifica o teu código e tenta de novo.'}
                </div>
              </div>
            </div>
          </div>
        </div>
         <p className="playground-note mono">Dica: troca o valor de <span style={{ color: 'hsl(67 88% 56%)' }}>nome</span> e executa outra vez.</p>
      </div>
    </section>
  );
}

function Documentation() {
  const [active, setActive] = useState<DocKey>('maps');
  const selected = docExamples[active];
  return (
    <section className="section section-rule" id="docs">
      <div className="container">
        <div className="docs-header">
          <div><p className="eyebrow">03 / Documentação</p><h2 className="display section-title">Aprende por exemplos que fazem sentido.</h2></div>
          <a className="btn btn-quiet" href="#getting-started" data-testid="link-read-docs">Ler a documentação <BookOpen size={15} /></a>
        </div>
        <div className="docs-tabs" role="tablist" aria-label="Exemplos de documentação">
          {(Object.keys(docExamples) as DocKey[]).map((key) => (
            <button key={key} className={`docs-tab ${active === key ? 'active' : ''}`} onClick={() => setActive(key)} role="tab" aria-selected={active === key} data-testid={`button-doc-tab-${key}`}>{docExamples[key].label}</button>
          ))}
        </div>
        <div className="docs-content">
          <div className="doc-explainer">
            <p className="eyebrow">{selected.kicker}</p>
            <h3>{selected.title}</h3>
            <p>{selected.body}</p>
            <a href="#getting-started" className="doc-link" data-testid="link-doc-example">ver no guia <ArrowUpRight size={13} /></a>
          </div>
          <div className="doc-code" data-testid="code-doc-example"><pre>{selected.code}</pre></div>
        </div>
      </div>
    </section>
  );
}

function Install() {
  const [copied, setCopied] = useState(false);
  const command = 'curl -fsSL hzhon.dev/install | sh';
  const copyCommand = async () => {
    try {
      await navigator.clipboard.writeText(command);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1800);
    } catch {
      setCopied(false);
    }
  };
  const platforms = [
    { name: 'Termux', detail: 'Leva Hzhon no teu Android, com o terminal que já conheces.', command: 'pkg install hzhon', icon: Smartphone },
    { name: 'Linux', detail: 'Binário nativo para a tua distribuição. Rápido e sem ruído.', command: 'sudo apt install hzhon', icon: Terminal },
    { name: 'macOS', detail: 'Instala com um comando e começa pelo teu editor favorito.', command: 'brew install hzhon', icon: Monitor },
    { name: 'Windows', detail: 'PowerShell, Windows Terminal ou o caminho que preferires.', command: 'winget install Hzhon', icon: Code2 },
  ];
  return (
    <section className="section install-section" id="getting-started">
      <div className="container install-layout">
        <div>
          <p className="eyebrow">04 / Primeiros passos</p>
          <h2 className="display install-title">Tira a ideia do browser.</h2>
          <p className="section-intro">O beta instala em poucos segundos. Depois, o terminal é teu espaço para experimentar.</p>
          <div className="install-command"><span>{command}</span><button className="copy-command" onClick={copyCommand} aria-label="Copiar comando de instalação" data-testid="button-copy-install">{copied ? <><Check size={14} /> Copiado</> : <><Copy size={14} /> Copiar</>}</button></div>
        </div>
        <div className="platforms">
          {platforms.map(({ name, detail, command: platformCommand, icon: Icon }) => (
            <article className="platform" key={name} data-testid={`card-platform-${name.toLowerCase()}`}>
              <div className="platform-head"><h4>{name}</h4><Icon size={18} aria-hidden="true" /></div>
              <p>{detail}</p>
              <code>{platformCommand}</code>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

function Roadmap() {
  const items = [
    { year: 'agora / beta', title: 'Uma base sólida', body: 'A linguagem que já podes instalar, explorar e discutir com a comunidade.', list: ['runtime + CLI', 'mapas e módulos', 'diagnósticos claros'], current: true },
    { year: 'próximo', title: 'Web sem tradução', body: 'Ferramentas para publicar ideias no browser, sem afastar-te do código.', list: ['web DSL', 'servidor local', 'componentes'], current: false },
    { year: 'a seguir', title: 'Mundos jogáveis', body: 'A ponte Hzhon-Luau para quem quer construir experiências no Roblox.', list: ['transpilador Luau', 'tipos Roblox', 'templates'], current: false },
    { year: 'mais adiante', title: 'Feita por muitos', body: 'Uma linguagem mais capaz porque mais vozes puderam ajudar a desenhá-la.', list: ['pacotes', 'editor tooling', 'comunidade lusófona'], current: false },
  ];
  return (
    <section className="section section-rule roadmap" id="roadmap">
      <div className="container">
        <div className="split-heading"><div><p className="eyebrow">05 / Roadmap</p><h2 className="display section-title">O mapa ainda está a ser desenhado.</h2></div><p className="section-intro">Beta significa espaço para mudar de ideias. Estes são os próximos lugares que queremos visitar contigo.</p></div>
        <div className="roadmap-track">
          {items.map((item) => <article className={`roadmap-item ${item.current ? 'current' : ''}`} key={item.year}><span className="roadmap-year">{item.year}</span><h4>{item.title}</h4><p>{item.body}</p><ul>{item.list.map((line) => <li key={line}>{line}</li>)}</ul></article>)}
        </div>
      </div>
    </section>
  );
}

function Ecosystem() {
  return (
    <section className="section ecosystem" id="ecosystem">
      <div className="container">
        <div className="split-heading"><div><p className="eyebrow">06 / Ecossistema</p><h2 className="display section-title">Não estás a aprender sozinho.</h2></div><p className="section-intro">Uma linguagem cresce quando encontra pessoas, ferramentas e histórias para continuar a sua conversa.</p></div>
        <div className="ecosystem-grid">
          <a className="eco-card" href="https://github.com" target="_blank" rel="noreferrer" data-testid="link-ecosystem-github"><div><span className="eco-symbol"><Github size={15} /></span><h4>Repositório aberto</h4><p>Vê o código, abre uma issue, propõe uma palavra melhor.</p></div><span className="eco-arrow"><ArrowUpRight size={18} /></span></a>
          <a className="eco-card" href="#docs" data-testid="link-ecosystem-guides"><div><span className="eco-symbol"><BookOpen size={15} /></span><h4>Guias de verdade</h4><p>Pequenos projetos e exemplos que não te deixam a meio.</p></div><span className="eco-arrow"><ChevronRight size={18} /></span></a>
          <a className="eco-card" href="#playground" data-testid="link-ecosystem-playground"><div><span className="eco-symbol"><Braces size={15} /></span><h4>Playground partilhável</h4><p>Experimenta uma ideia e leva o resultado para alguém.</p></div><span className="eco-arrow"><ExternalLink size={17} /></span></a>
        </div>
      </div>
    </section>
  );
}

function Footer() {
  return (
    <footer className="footer">
      <div className="container footer-inner">
        <p>Hzhon — uma linguagem em português, feita em comunidade.</p>
        <div className="footer-links"><a href="#top" data-testid="link-footer-top">voltar ao topo</a><a href="https://github.com" target="_blank" rel="noreferrer" data-testid="link-footer-github">github</a><a href="#roadmap" data-testid="link-footer-roadmap">roadmap</a></div>
      </div>
    </footer>
  );
}

function Home() {
  return <div className="site-shell noise"><Nav /><main><Hero /><LanguageSection /><Playground /><Documentation /><Install /><Roadmap /><Ecosystem /></main><Footer /></div>;
}

function Router() {
  return <RoutedErrorBoundary><Switch><Route path="/" component={Home} /><Route component={NotFound} /></Switch></RoutedErrorBoundary>;
}

function RoutedErrorBoundary({ children }: { children: ReactNode }) {
  const [location] = useLocation();
  return <ErrorBoundary resetKey={location}>{children}</ErrorBoundary>;
}

function App() {
  return <QueryClientProvider client={queryClient}><TooltipProvider><WouterRouter base={import.meta.env.BASE_URL.replace(/\/$/, '')}><Router /></WouterRouter><Toaster /></TooltipProvider></QueryClientProvider>;
}

export default App;
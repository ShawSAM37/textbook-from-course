export const meta = {
  name: 'textbook-chapters',
  description: 'Write the chapters of a textbook project in parallel (author, optional partner), review each chapter with three independent reviewers, then fix',
  whenToUse: 'After the textbook-from-course project is planned: book.json filled, chapter briefs written, skeletons created with tb.py new-book, pilot approved',
  phases: [
    { title: 'Author', detail: 'one author per chapter (+ partner for split chapters): content, objectives, summary, key terms, questions, answers' },
    { title: 'Verify', detail: 'three independent reviewers per chapter: solutions correctness, identity and voice, layout' },
    { title: 'Fix', detail: 'one fixer per chapter applies the confirmed findings and re-runs every check' },
  ],
}

// args = { project, skill, book, chapters: [ {file, number, title, short, total, own, partner:{file,budget}|null, brief} ], model? }
const A = args
if (!A || !A.project || !A.skill || !A.book || !Array.isArray(A.chapters) || A.chapters.length === 0) {
  throw new Error('book-workflow.js needs args {project, skill, book, chapters:[...]} - see references/pipeline.md')
}
const P = A.project
const S = A.skill
const BOOK = A.book
const withModel = (o) => (A.model ? { ...o, model: A.model } : o)   // default: inherit the session model (never a higher tier)

const TB = (cmd) => `python "${S}/scripts/tb.py" --project "${P}" ${cmd}`
const chapterFile = (c) => `${P}/${BOOK}/${c.file}.tex`

const COMMON = (c) => String.raw`Project folder: ${P}. Skill folder: ${S}. Book id: ${BOOK}. Chapter file ${chapterFile(c)} (printed chapter ${c.number}, title "${c.title}", short header title "${c.short}"). Whole-chapter page budget: ${c.total} pages${c.partner ? ` (owner file at most ${c.own}, part file ${c.partner.file}.tex at most ${c.partner.budget})` : ''}. Chapter brief: ${P}/${c.brief}. Read ${S}/references/chapter-spec.md completely before you start; ${S}/references/agent-briefs.md describes your role; ${S}/references/pitfalls.md lists traps (write .tex/.py/.json with the Write tool, not shell heredocs). Run tools as: ${TB('<command>')} (for example ${TB('check ' + BOOK + ' ' + c.file + ' --budget ' + c.total)}).`

const AUTHOR = (c) => String.raw`You are the AUTHOR of one chapter. Follow agent-briefs.md section 3 (Author) exactly. ${COMMON(c)}${c.partner ? ` A partner author polishes/writes ${c.partner.file}.tex concurrently: read it, never edit it; if a compile error points into it, retry later or verify your own part with a private copy that omits its input.` : ''}
Deliver the chapter to the structure of chapter-spec.md section 1 (introduction, objectives, sections of connected prose, summary, key terms, review questions, practice questions, complete self-contained answers) in the published-book voice of section 7, inside the page ceiling but without dropping any source content (log omissions), technically correct, with every number recomputed by script, verified with tb.py check (PROBLEMS: 0), tb.py scrub (0 findings) and tb.py voice (answered), and every page with a figure/table/code/box looked at. Return the structured report (exercises = number of questions, solutions = number of answers).`

const PARTNER = (c) => String.raw`You are the PARTNER author. Follow agent-briefs.md section 4 (Partner). ${COMMON(c)} Your file is ${P}/${BOOK}/${c.partner ? c.partner.file : ''}.tex (sections only, budget ${c.partner ? c.partner.budget : 0} pages); the owner writes the chapter head, objectives, summary, questions and answers; its skeleton already inputs your file before the Summary. Verify with ${TB('check ' + BOOK + ' ' + (c.partner ? c.partner.file : '') + ' --budget ' + (c.partner ? c.partner.budget : 0))} and tb.py scrub. Return the structured report.`

const LENS = {
  solutions: (c) => String.raw`You are an INDEPENDENT REVIEWER (read-only; do not edit chapter files). Follow agent-briefs.md section 8, role "Reviewer: solutions". ${COMMON(c)} Try to refute the questions and answers; recompute every number yourself; report only real defects with location, quoted fragment, why wrong and corrected content. Return structured findings.`,
  voice: (c) => String.raw`You are an INDEPENDENT REVIEWER (read-only; do not edit chapter files). Follow agent-briefs.md section 8, role "Reviewer: identity and voice". ${COMMON(c)} Run tb.py scrub and tb.py voice yourself and also read the prose and open the figures used. Return structured findings.`,
  layout: (c) => String.raw`You are an INDEPENDENT REVIEWER (read-only for chapter files; scratch files under ${P}/build are fine). Follow agent-briefs.md section 8, role "Reviewer: layout and completeness". ${COMMON(c)} Run the check yourself, compare against the coverage ledger, and LOOK at every page. Return structured findings.`,
}

const FIX = (c, findings, author) => String.raw`You are the FIXER. Follow agent-briefs.md section 8, role "Fixer". ${COMMON(c)} Verify every finding before acting; fix all valid high and medium findings and the cheap lows within the budget; return findings that need a style change instead of editing it; re-run tb.py check (PROBLEMS: 0) and tb.py scrub (0 findings), recompute changed numbers, look at changed pages.
The author's report: ${JSON.stringify(author)}
FINDINGS: ${JSON.stringify(findings)}
Return the structured report.`

const AUTHOR_SCHEMA = { type: 'object', properties: { status: { type: 'string' }, pages_total: { type: 'number' }, pages_budget: { type: 'number' }, exercises: { type: 'number' }, solutions: { type: 'number' }, audit_problems: { type: 'number' }, scrub_findings: { type: 'number' }, notes: { type: 'string' } }, required: ['status', 'pages_total', 'pages_budget', 'exercises', 'solutions', 'audit_problems', 'scrub_findings', 'notes'] }
const PARTNER_SCHEMA = { type: 'object', properties: { status: { type: 'string' }, pages: { type: 'number' }, budget: { type: 'number' }, audit_problems: { type: 'number' }, scrub_findings: { type: 'number' }, notes: { type: 'string' } }, required: ['status', 'pages', 'budget', 'audit_problems', 'scrub_findings', 'notes'] }
const FINDINGS_SCHEMA = { type: 'object', properties: { lens: { type: 'string' }, summary: { type: 'string' }, findings: { type: 'array', items: { type: 'object', properties: { severity: { type: 'string' }, where: { type: 'string' }, problem: { type: 'string' }, fix: { type: 'string' } }, required: ['severity', 'where', 'problem', 'fix'] } } }, required: ['lens', 'summary', 'findings'] }
const FIX_SCHEMA = { type: 'object', properties: { status: { type: 'string' }, pages_total: { type: 'number' }, audit_problems: { type: 'number' }, scrub_findings: { type: 'number' }, fixed: { type: 'number' }, unfixed: { type: 'array', items: { type: 'string' } }, notes: { type: 'string' } }, required: ['status', 'pages_total', 'audit_problems', 'scrub_findings', 'fixed', 'unfixed', 'notes'] }

phase('Author')
log('Authors for ' + A.chapters.length + ' chapter(s) of book ' + BOOK)

const results = await pipeline(
  A.chapters,
  async (c) => {
    const jobs = [() => agent(AUTHOR(c), withModel({ label: 'author:' + c.file, phase: 'Author', schema: AUTHOR_SCHEMA }))]
    if (c.partner) jobs.push(() => agent(PARTNER(c), withModel({ label: 'partner:' + c.file, phase: 'Author', schema: PARTNER_SCHEMA })))
    const [author, partner] = await parallel(jobs)
    log(c.file + ' authored: ' + JSON.stringify({ status: author && author.status, pages: author && author.pages_total }))
    return { c, author, partner: partner || null }
  },
  async (r) => {
    if (!r.author) return { ...r, findings: null }
    const outs = await parallel(['solutions', 'voice', 'layout'].map((l) => () =>
      agent(LENS[l](r.c), withModel({ label: 'verify-' + l + ':' + r.c.file, phase: 'Verify', schema: FINDINGS_SCHEMA }))))
    const findings = outs.filter(Boolean)
    log(r.c.file + ' verified: ' + findings.reduce((n, f) => n + f.findings.length, 0) + ' findings')
    return { ...r, findings }
  },
  async (r) => {
    if (!r.author || !r.findings) return { ...r, fix: null }
    const all = r.findings.flatMap((f) => f.findings.map((x) => ({ lens: f.lens, ...x })))
    if (all.length === 0) return { ...r, fix: { status: 'nothing to fix' } }
    const fix = await agent(FIX(r.c, all, r.author), withModel({ label: 'fix:' + r.c.file, phase: 'Fix', schema: FIX_SCHEMA }))
    log(r.c.file + ' fixed: ' + JSON.stringify(fix && { status: fix.status, pages: fix.pages_total, problems: fix.audit_problems }))
    return { ...r, fix }
  },
)

return results.map((r) => r && ({
  chapter: r.c.file,
  author: r.author,
  partner: r.partner,
  reviewers: r.findings && r.findings.map((f) => ({ lens: f.lens, n: f.findings.length, high: f.findings.filter((x) => x.severity === 'high').length, summary: f.summary })),
  fix: r.fix,
}))

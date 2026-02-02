import { useMemo, useState } from 'react'

function BrandMark() {
  return (
    <div className="flex items-center gap-3">
      <div className="h-9 w-9 border border-gray-900 bg-white grid place-items-center">
        <div className="h-3 w-3 bg-brand-600" />
      </div>
      <div className="leading-tight">
        <div className="text-sm font-semibold tracking-swiss">NEWSLETTER FACTORY</div>
        <div className="text-xs text-gray-500">AI investments • events • signals</div>
      </div>
    </div>
  )
}

function PreviewItem({ title, meta, tags }) {
  return (
    <div className="py-4 border-b border-gray-200 last:border-b-0">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="text-sm font-semibold text-gray-900">{title}</div>
          <div className="mt-1 text-xs text-gray-500">{meta}</div>
        </div>
        <div className="flex flex-wrap justify-end gap-2">
          {tags.map((t) => (
            <span key={t} className="ui-pill">{t}</span>
          ))}
        </div>
      </div>
    </div>
  )
}

export default function App() {
  const [email, setEmail] = useState('')
  const [frequency, setFrequency] = useState('weekly')
  const [topics, setTopics] = useState({ investments: true, events: true })
  const [submitted, setSubmitted] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState('')

  const subscribeWebhookUrl = (import.meta.env.VITE_SUBSCRIBE_WEBHOOK_URL || '').trim()

  const canSubmit = useMemo(() => {
    const hasEmail = /.+@.+\..+/.test(email)
    const hasTopic = Object.values(topics).some(Boolean)
    return hasEmail && hasTopic
  }, [email, topics])

  return (
    <div className="min-h-screen font-sans">
      <div className="min-h-screen bg-gray-50">
        <div className="h-1 w-full bg-brand-600" />
        <header className="border-b border-gray-200 bg-white/80 backdrop-blur">
          <div className="ui-container py-6 flex items-center justify-between">
            <BrandMark />
            <div className="flex items-center gap-3">
              <a className="text-sm text-gray-700 hover:text-gray-900" href="#preview">Preview</a>
              <a className="text-sm text-gray-700 hover:text-gray-900" href="#signup">Sign up</a>
              <span className="ui-pill">Prototype</span>
            </div>
          </div>
        </header>

        <main className="ui-container py-12 sm:py-16">
          <div className="grid grid-cols-1 gap-8 lg:grid-cols-12 lg:gap-10 items-start">
            <section className="lg:col-span-7">
              <div className="ui-card ui-card-pad">
                <div className="flex items-start justify-between gap-6">
                  <div>
                    <h1 className="text-4xl sm:text-5xl font-bold tracking-swiss leading-[1.05]">
                      A clean, evidence‑first AI newsletter.
                    </h1>
                    <p className="mt-4 text-base sm:text-lg text-gray-600 max-w-prose">
                      Short, factual digests from sources like TechCrunch — filtered for AI relevance and grounded with links.
                    </p>
                  </div>
                  <div className="hidden sm:block">
                    <div className="h-10 w-10 border border-gray-900 bg-white grid place-items-center shadow-crisp">
                      <div className="h-4 w-4 bg-brand-600" />
                    </div>
                  </div>
                </div>

                <div className="mt-8 flex flex-wrap gap-3">
                  <span className="ui-pill">No invented dates</span>
                  <span className="ui-pill">AI-only filter</span>
                  <span className="ui-pill">Evidence links</span>
                  <span className="ui-pill">Email-ready (.eml)</span>
                </div>

                <div className="mt-10 flex items-center gap-3">
                  <a href="#signup" className="ui-btn">Get the newsletter</a>
                  <a href="#preview" className="ui-btn ui-btn-secondary">See a preview</a>
                </div>
              </div>

              <div id="preview" className="mt-8 ui-card ui-card-pad">
                <div className="flex items-start justify-between gap-6">
                  <div>
                    <h2 className="text-xl font-semibold tracking-swiss">Latest preview</h2>
                    <p className="mt-1 text-sm text-gray-600">A compact sample of what subscribers receive.</p>
                  </div>
                  <div className="text-xs text-gray-500">Feb 2, 2026</div>
                </div>

                <div className="mt-6">
                  <PreviewItem
                    title="TechCrunch: AI infrastructure startup raises $50M"
                    meta="Investment • Source link included"
                    tags={["Investment", "AI Infra", "Evidence"]}
                  />
                  <PreviewItem
                    title="NYC meetup: Responsible AI in production"
                    meta="Event • Real date required"
                    tags={["Event", "NYC", "Governance"]}
                  />
                </div>
              </div>
            </section>

            <aside id="signup" className="lg:col-span-5 lg:sticky lg:top-8">
              <div className="ui-card ui-card-pad">
                <div className="flex items-start justify-between gap-6">
                  <div>
                    <h2 className="text-xl font-semibold tracking-swiss">Subscribe</h2>
                    <p className="mt-1 text-sm text-gray-600">Choose frequency and what you care about.</p>
                  </div>
                  <div className="ui-pill">Free</div>
                </div>

                {submitted ? (
                  <div className="mt-6 border border-gray-200 bg-white p-4">
                    <div className="text-sm font-semibold">You’re on the list (demo).</div>
                    <div className="mt-1 text-sm text-gray-600">
                      Next step: wire this to a backend + email service.
                    </div>
                    <button className="mt-4 ui-btn ui-btn-secondary" onClick={() => setSubmitted(false)}>
                      Add another email
                    </button>
                  </div>
                ) : (
                  <form
                    className="mt-6 space-y-6"
                    onSubmit={(e) => {
                      ;(async () => {
                        e.preventDefault()
                        if (!canSubmit || submitting) return

                        setSubmitError('')
                        setSubmitting(true)

                        try {
                          const payload = {
                            email,
                            frequency,
                            topics,
                            source: 'newsletter-ui',
                            createdAt: new Date().toISOString(),
                          }

                          // Simplest + most efficient “backend” for demo: Zapier Catch Hook.
                          // If no webhook is configured, behave as a local prototype.
                          if (subscribeWebhookUrl) {
                            await fetch(subscribeWebhookUrl, {
                              method: 'POST',
                              mode: 'no-cors',
                              headers: {
                                'Content-Type': 'application/json',
                              },
                              body: JSON.stringify(payload),
                            })
                          }

                          setSubmitted(true)
                        } catch (err) {
                          setSubmitError('Could not subscribe right now. Please try again.')
                        } finally {
                          setSubmitting(false)
                        }
                      })()
                    }}
                  >
                    <div className="space-y-2">
                      <label className="ui-label" htmlFor="email">Email</label>
                      <input
                        id="email"
                        className="ui-input"
                        type="email"
                        placeholder="you@company.com"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                      />
                      <div className="ui-hint">One email, one newsletter. Unsubscribe anytime.</div>
                    </div>

                    <fieldset className="space-y-3">
                      <legend className="ui-label">Frequency</legend>
                      <div className="grid grid-cols-2 gap-3">
                        <label className="flex items-center gap-2 border border-gray-200 px-3 py-2 cursor-pointer hover:bg-gray-50">
                          <input
                            type="radio"
                            name="frequency"
                            value="weekly"
                            checked={frequency === 'weekly'}
                            onChange={() => setFrequency('weekly')}
                            className="accent-brand-600"
                          />
                          <span className="text-sm">Weekly <span className="text-xs text-gray-500">(recommended)</span></span>
                        </label>
                        <label className="flex items-center gap-2 border border-gray-200 px-3 py-2 cursor-pointer hover:bg-gray-50">
                          <input
                            type="radio"
                            name="frequency"
                            value="monthly"
                            checked={frequency === 'monthly'}
                            onChange={() => setFrequency('monthly')}
                            className="accent-brand-600"
                          />
                          <span className="text-sm">Monthly</span>
                        </label>
                      </div>
                      <div className="ui-hint">You can change this later.</div>
                    </fieldset>

                    <fieldset className="space-y-3">
                      <legend className="ui-label">Topics</legend>
                      <div className="space-y-2">
                        <label className="flex items-center justify-between border border-gray-200 px-3 py-2 hover:bg-gray-50 cursor-pointer">
                          <span className="text-sm">AI investments & funding</span>
                          <input
                            type="checkbox"
                            className="accent-brand-600"
                            checked={topics.investments}
                            onChange={(e) => setTopics((t) => ({ ...t, investments: e.target.checked }))}
                          />
                        </label>
                        <label className="flex items-center justify-between border border-gray-200 px-3 py-2 hover:bg-gray-50 cursor-pointer">
                          <span className="text-sm">AI events & meetups</span>
                          <input
                            type="checkbox"
                            className="accent-brand-600"
                            checked={topics.events}
                            onChange={(e) => setTopics((t) => ({ ...t, events: e.target.checked }))}
                          />
                        </label>
                      </div>
                      {!Object.values(topics).some(Boolean) ? (
                        <div className="text-xs text-brand-700">Pick at least one topic.</div>
                      ) : null}
                    </fieldset>

                    <div className="flex items-center gap-3">
                      <button className="ui-btn" type="submit" disabled={!canSubmit || submitting}>
                        {submitting ? 'Subscribing…' : 'Subscribe'}
                      </button>
                      <button
                        className="ui-btn ui-btn-secondary"
                        type="button"
                        onClick={() => {
                          setEmail('')
                          setFrequency('weekly')
                          setTopics({ investments: true, events: true })
                          setSubmitError('')
                        }}
                      >
                        Reset
                      </button>
                    </div>

                    {submitError ? (
                      <div className="text-sm text-brand-700">{submitError}</div>
                    ) : null}

                    <div className="text-xs text-gray-500">
                      {subscribeWebhookUrl
                        ? 'Connected to automation webhook.'
                        : 'Prototype mode: set VITE_SUBSCRIBE_WEBHOOK_URL to capture signups in Zapier.'}
                    </div>
                  </form>
                )}
              </div>
            </aside>
          </div>
        </main>

        <footer className="border-t border-gray-200 bg-white">
          <div className="ui-container py-8 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div className="text-sm text-gray-600">
              Built for demo: polished UI now, backend + sending next.
            </div>
            <div className="text-xs text-gray-500">© 2026 Newsletter Factory</div>
          </div>
        </footer>
      </div>
    </div>
  )
}

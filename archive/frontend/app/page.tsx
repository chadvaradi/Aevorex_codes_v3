import { Button } from "../branding/launch-ui-pro-2.3.3/ui/button";
import { Input } from "../branding/launch-ui-pro-2.3.3/ui/input";

export default function HomePage() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Header */}
      <header className="border-b border-border/10 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-16 items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-primary"></div>
            <span className="font-bold">Luna</span>
          </div>
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="sm">
              Login
            </Button>
            <Button size="sm">
              Join waitlist
            </Button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container py-24">
        <div className="mx-auto max-w-4xl text-center">
          <h1 className="text-4xl font-bold tracking-tight sm:text-6xl">
            Build MCP servers on a global edge network
          </h1>
          <p className="mt-6 text-lg text-muted-foreground">
            Our platform enables you to quickly deploy MCP servers with global distribution, 
            advanced caching, and optimized performance on our worldwide edge infrastructure.
          </p>
          
          <div className="mt-8 flex flex-col items-center gap-4">
            <form className="flex w-full max-w-[420px] gap-2">
              <Input
                type="email"
                placeholder="Email address"
                className="border-border/10 bg-foreground/10 grow"
              />
              <Button variant="default" size="lg">
                Join waitlist
              </Button>
            </form>
            <p className="text-muted-foreground text-xs">
              We&apos;ll notify you when we launch.
            </p>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="container py-24">
        <div className="mx-auto max-w-4xl text-center">
          <h2 className="text-3xl font-bold tracking-tight">
            Industry-leading performance
          </h2>
          <p className="mt-4 text-muted-foreground">
            Our MCP servers offer exceptional speed and reliability, powering thousands of applications across the globe.
          </p>
          
          <div className="mt-12 grid grid-cols-1 gap-8 sm:grid-cols-3">
            <div className="text-center">
              <div className="text-3xl font-bold text-primary">99.99%</div>
              <div className="mt-2 font-semibold">Uptime guarantee</div>
              <div className="mt-1 text-sm text-muted-foreground">
                We ensure maximum availability of your MCP servers
              </div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-primary">10,000+</div>
              <div className="mt-2 font-semibold">Active deployments</div>
              <div className="mt-1 text-sm text-muted-foreground">
                Trusted by developers across industries
              </div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-primary">200+</div>
              <div className="mt-2 font-semibold">Edge locations</div>
              <div className="mt-1 text-sm text-muted-foreground">
                Global network presence for reduced latency
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Logos Section */}
      <section className="container py-24">
        <div className="mx-auto max-w-4xl text-center">
          <h2 className="text-2xl font-bold tracking-tight">
            Trusted by technology-forward organizations
          </h2>
          <div className="mt-12 grid grid-cols-2 gap-8 sm:grid-cols-4">
            <div className="flex items-center justify-center">
              <div className="h-8 w-24 rounded bg-muted"></div>
            </div>
            <div className="flex items-center justify-center">
              <div className="h-8 w-24 rounded bg-muted"></div>
            </div>
            <div className="flex items-center justify-center">
              <div className="h-8 w-24 rounded bg-muted"></div>
            </div>
            <div className="flex items-center justify-center">
              <div className="h-8 w-24 rounded bg-muted"></div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border/10 bg-background/95">
        <div className="container py-12">
          <div className="text-center text-sm text-muted-foreground">
            © 2024 Luna. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
}
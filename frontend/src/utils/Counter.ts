export default class Counter<T> {
  private counter: Map<T, number>;

  constructor(iterable?: Iterable<T>) {
    this.counter = new Map<T, number>();
    if (iterable) {
      for (const item of iterable) {
        this.update(item);
      }
    }
  }

  update(item: T): void {
    const count = this.counter.get(item) || 0;
    this.counter.set(item, count + 1);
  }

  subtract(item: T): void {
    const count = this.counter.get(item) || 0;
    if (count > 1) {
      this.counter.set(item, count - 1);
    } else {
      this.counter.delete(item);
    }
  }

  getCount(item: T): number {
    return this.counter.get(item) || 0;
  }

  mostCommon(n: number = 10): [T, number][] {
    const items = Array.from(this.counter.entries());
    items.sort((a, b) => b[1] - a[1]);
    return items.slice(0, n);
  }

  elements(): T[] {
    const elements: T[] = [];
    for (const [item, count] of this.counter.entries()) {
      for (let i = 0; i < count; i++) {
        elements.push(item);
      }
    }
    return elements;
  }

  keys(): T[] {
    return Array.from(this.counter.keys());
  }

  values(): number[] {
    return Array.from(this.counter.values());
  }

  toString(): string {
    const items = Array.from(this.counter.entries()).map(([item, count]) => `${item}: ${count}`);
    return `{${items.join(', ')}}`;
  }
}
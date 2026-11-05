import { defineConfig } from 'astro/config';

// https://astro.build/config
export default defineConfig({
  site: 'https://wxz.zxw.ac.cn',
  output: 'static',
  build: {
    format: 'file'
  }
});

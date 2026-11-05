import { defineCollection, z } from 'astro:content';

const newsCollection = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string().optional().default('新闻动态'),
    date: z.any().optional(),
    id: z.any().optional(),
    coverImage: z.string().optional(),
    description: z.string().optional(),
    image: z.string().optional()
  }).passthrough()
});

export const collections = {
  'news': newsCollection
};

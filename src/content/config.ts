import { defineCollection, z } from 'astro:content';

const newsCollection = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    date: z.string().or(z.date()),
    id: z.string().optional(),
    coverImage: z.string().optional(),
    description: z.string().optional(),
    image: z.string().optional()
  })
});

export const collections = {
  'news': newsCollection
};

'use client';

import {useState} from 'react';
import {useLocale, useTranslations} from 'next-intl';
import {zodResolver} from '@hookform/resolvers/zod';
import {useForm} from 'react-hook-form';
import {z} from 'zod';
import type {Locale} from '@/i18n/routing';
import type {FeedbackType} from '@/lib/api-types';
import {sendFeedback} from '@/lib/feedback';
import {Button} from './Button';

type Values = {full_name:string;company:string;country:string;email:string;phone:string;subject:string;message:string;consent:boolean;website:string};
const schema = z.object({
  full_name:z.string().trim().min(2).max(150), company:z.string().trim().min(1).max(200),
  country:z.string().trim().min(1).max(100), email:z.email(), phone:z.string().max(30).regex(/^[+\d\s()-]*$/),
  subject:z.string().trim().min(1).max(200), message:z.string().trim().min(10).max(5000),
  consent:z.boolean().refine(Boolean), website:z.string()
});
const control='w-full min-w-0 rounded-md border border-border bg-white px-3 py-2 text-text';
const fields = [
  {name:'full_name',required:true},{name:'company',required:true},{name:'country',required:true},
  {name:'email',required:true,type:'email'},{name:'phone',required:false},
  {name:'subject',required:true},{name:'message',required:true}
] as const;

export function FeedbackForm({type,defaultSubject=''}:{type:FeedbackType;defaultSubject?:string}) {
  const t=useTranslations('Feedback'); const locale=useLocale() as Locale; const [success,setSuccess]=useState(false);
  const {register,handleSubmit,setError,formState:{errors,isSubmitting}}=useForm<Values>({resolver:zodResolver(schema),defaultValues:{full_name:'',company:'',country:'',email:'',phone:'',subject:defaultSubject,message:'',consent:false,website:''}});
  const submit=async(values:Values)=>{
    const result=await sendFeedback({...values,phone:values.phone||null,type,lang:locale});
    if(result.ok){setSuccess(true);return;}
    if(result.status===429){setError('root',{message:t('tooMany')});return;}
    if(result.status===400&&'errors' in result){
      for(const [field,messages] of Object.entries(result.errors)){
        if(field in values && messages?.[0]) setError(field as keyof Values,{message:messages[0]});
      }
      return;
    }
    setError('root',{message:t('error')});
  };
  if(success)return <p role="status" className="rounded-lg bg-primary-light p-6 text-text">{t('success')}</p>;
  return <form onSubmit={handleSubmit(submit)} className="relative grid min-w-0 gap-5 sm:grid-cols-2" noValidate>
    {fields.map(({name,required})=><div key={name} className={`min-w-0 ${name==='message'?'sm:col-span-2':''}`}>
      <label htmlFor={name} className="mb-1 block font-medium">{t(`fields.${name}`)}{required?' *':''}</label>
      {name==='message'?<textarea id={name} rows={5} className={control} {...register(name)}/>:<input id={name} type={name==='email'?'email':'text'} className={control} {...register(name)}/>}
      {errors[name]&&<p className="mt-1 text-sm text-red-700">{t('invalid')}</p>}
    </div>)}
    {/* honeypot: не display:none — часть ботов такие поля пропускает; прячем за экран */}
    <div aria-hidden="true" className="absolute -left-[10000px] size-px overflow-hidden"><label htmlFor="website">Website</label><input id="website" type="text" tabIndex={-1} autoComplete="off" {...register('website')}/></div>
    <div className="sm:col-span-2"><label className="flex items-start gap-3"><input type="checkbox" className="mt-1" {...register('consent')}/><span>{t('consent')}</span></label>{errors.consent&&<p className="mt-1 text-sm text-red-700">{t('required')}</p>}</div>
    <div className="sm:col-span-2"><Button type="submit" disabled={isSubmitting}>{isSubmitting?t('sending'):t('submit')}</Button>{errors.root&&<p role="alert" className="mt-2 text-sm text-red-700">{errors.root.message}</p>}</div>
  </form>;
}

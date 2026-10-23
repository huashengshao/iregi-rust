
target/native-stack-batch/probe-fixed-c0:     file format elf64-x86-64


Disassembly of section .text:

00000000001d53d0 <_RINvNtNtCs6nLMqq22G8J_21native_stack_fixed_c09generated8baseline12batch_body_1dEB6_>:
  1d53d0:	push   %rbp
  1d53d1:	push   %r15
  1d53d3:	push   %r14
  1d53d5:	push   %r13
  1d53d7:	push   %r12
  1d53d9:	push   %rbx
  1d53da:	sub    $0x78,%rsp
  1d53de:	mov    %rdx,%r12
  1d53e1:	mov    %rsi,%rbx
  1d53e4:	mov    0xb0(%rsp),%rdx
  1d53ec:	lea    (%r12,%r12,1),%rsi
  1d53f0:	sub    %rsi,%rdx
  1d53f3:	jb     1d6614 <_RINvNtNtCs6nLMqq22G8J_21native_stack_fixed_c09generated8baseline12batch_body_1dEB6_+0x1244>
  1d53f9:	cmp    %rdx,%rsi
  1d53fc:	ja     1d65db <_RINvNtNtCs6nLMqq22G8J_21native_stack_fixed_c09generated8baseline12batch_body_1dEB6_+0x120b>
  1d5402:	mov    %r8,%r13
  1d5405:	cmp    %r12,%r8
  1d5408:	ja     1d65ea <_RINvNtNtCs6nLMqq22G8J_21native_stack_fixed_c09generated8baseline12batch_body_1dEB6_+0x121a>
  1d540e:	mov    %rdi,%r14
  1d5411:	mov    %rsi,0x30(%rsp)
  1d5416:	mov    %r9,0x70(%rsp)
  1d541b:	lea    (%r9,%rsi,8),%rdi
  1d541f:	lea    (%rdi,%r12,8),%rbp
  1d5423:	lea    0x0(,%r13,8),%r15
  1d542b:	mov    %rdi,0x18(%rsp)
  1d5430:	mov    %rcx,%rsi
  1d5433:	mov    %r15,%rdx
  1d5436:	mov    %rcx,0x48(%rsp)
  1d543b:	call   *0x297aa37(%rip)        # 2b4fe78 <memcpy@GLIBC_2.14>
  1d5441:	mov    %rbp,%r10
  1d5444:	mov    %r15,%r11
  1d5447:	mov    0x48(%rsp),%r9
  1d544c:	xor    %eax,%eax
  1d544e:	xchg   %ax,%ax
  1d5450:	mov    (%r9,%rax,1),%rdi
  1d5454:	cmp    %r12,%rdi
  1d5457:	jae    1d662d <_RINvNtNtCs6nLMqq22G8J_21native_stack_fixed_c09generated8baseline12batch_body_1dEB6_+0x125d>
  1d545d:	movq   $0x0,(%r10,%rdi,8)
  1d5465:	add    $0x8,%rax
  1d5469:	cmp    %rax,%r11
  1d546c:	jne    1d5450 <_RINvNtNtCs6nLMqq22G8J_21native_stack_fixed_c09generated8baseline12batch_body_1dEB6_+0x80>
  1d546e:	mov    0x30(%rsp),%rax
  1d5473:	lea    (%rax,%rax,4),%rax
  1d5477:	mov    %rax,0x20(%rsp)
  1d547c:	lea    (%r12,%r12,2),%rax
  1d5480:	lea    (%r12,%rax,4),%rsi
  1d5484:	mov    %r12,%r15
  1d5487:	shl    $0x4,%r15
  1d548b:	xor    %edx,%edx
  1d548d:	mov    0x18(%rsp),%r8
  1d5492:	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
  1d54a0:	mov    (%r8,%rdx,1),%rdi
  1d54a4:	mov    0x20(%rsp),%rax
  1d54a9:	add    %rdi,%rax
  1d54ac:	cmp    %rbx,%rax
  1d54af:	jae    1d6660 <_RINvNtNtCs6nLMqq22G8J_21native_stack_fixed_c09generated8baseline12batch_body_1dEB6_+0x1290>
  1d54b5:	lea    (%rdi,%rsi,1),%rcx
  1d54b9:	cmp    %rbx,%rcx
  1d54bc:	jae    1d664d <_RINvNtNtCs6nLMqq22G8J_21native_stack_fixed_c09generated8baseline12batch_body_1dEB6_+0x127d>
  1d54c2:	add    %r15,%rdi
  1d54c5:	cmp    %rbx,%rdi
  1d54c8:	jae    1d663d <_RINvNtNtCs6nLMqq22G8J_21native_stack_fixed_c09generated8baseline12batch_body_1dEB6_+0x126d>
  1d54ce:	shl    $0x4,%rax
  1d54d2:	shl    $0x4,%rcx
  1d54d6:	shl    $0x4,%rdi
  1d54da:	movupd (%r14,%rax,1),%xmm0
  1d54e0:	movsd  (%r14,%rcx,1),%xmm1
  1d54e6:	movsd  0x8(%r14,%rcx,1),%xmm2
  1d54ed:	unpcklpd %xmm1,%xmm1
  1d54f1:	mulpd  %xmm0,%xmm1
  1d54f5:	shufpd $0x1,%xmm0,%xmm0
  1d54fa:	unpcklpd %xmm2,%xmm2
  1d54fe:	mulpd  %xmm0,%xmm2
  1d5502:	movapd %xmm1,%xmm0
  1d5506:	subpd  %xmm2,%xmm0
  1d550a:	addpd  %xmm1,%xmm2
  1d550e:	movsd  %xmm0,%xmm2
  1d5512:	movupd %xmm2,(%r14,%rdi,1)
  1d5518:	add    $0x8,%rdx
  1d551c:	cmp    %rdx,%r11
  1d551f:	jne    1d54a0 <_RINvNtNtCs6nLMqq22G8J_21native_stack_fixed_c09generated8baseline12batch_body_1dEB6_+0xd0>
  1d5525:	lea    0x0(,%r12,8),%rdx
  1d552d:	sub    %r12,%rdx
  1d5530:	xor    %ecx,%ecx
  1d5532:	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
  1d5540:	mov    (%r8,%rcx,1),%rdi
  1d5544:	lea    (%rdi,%rdx,1),%rax
  1d5548:	cmp    %rbx,%rax
  1d554b:	jae    1d6683 <_RINvNtNtCs6nLMqq22G8J_21native_stack_fixed_c09generated8baseline12batch_body_1dEB6_+0x12b3>
  1d5551:	add    %r15,%rdi
  1d5554:	cmp    %rbx,%rdi
  1d5557:	jae    1d6673 <_RINvNtNtCs6nLMqq22G8J_21native_stack_fixed_c09generated8baseline12batch_body_1dEB6_+0x12a3>
  1d555d:	shl    $0x4,%rax
  1d5561:	shl    $0x4,%rdi
  1d5565:	movupd (%r14,%rax,1),%xmm0
  1d556b:	movupd (%r14,%rdi,1),%xmm1
  1d5571:	addpd  %xmm0,%xmm1
  1d5575:	movupd %xmm1,(%r14,%rdi,1)
  1d557b:	add    $0x8,%rcx
  1d557f:	cmp    %rcx,%r11
  1d5582:	jne    1d5540 <_RINvNtNtCs6nLMqq22G8J_21native_stack_fixed_c09generated8baseline12batch_body_1dEB6_+0x170>

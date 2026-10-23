
target/native-shared-binary/probe:     file format elf64-x86-64


Disassembly of section .text:

00000000013c28d0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>>:
 13c28d0:	55                   	push   %rbp
 13c28d1:	41 57                	push   %r15
 13c28d3:	41 56                	push   %r14
 13c28d5:	41 55                	push   %r13
 13c28d7:	41 54                	push   %r12
 13c28d9:	53                   	push   %rbx
 13c28da:	48 83 ec 58          	sub    $0x58,%rsp
 13c28de:	48 89 f8             	mov    %rdi,%rax
 13c28e1:	4c 8b b4 24 b8 00 00 	mov    0xb8(%rsp),%r14
 13c28e8:	00 
 13c28e9:	4c 8b 94 24 b0 00 00 	mov    0xb0(%rsp),%r10
 13c28f0:	00 
 13c28f1:	4c 8b 9c 24 a0 00 00 	mov    0xa0(%rsp),%r11
 13c28f8:	00 
 13c28f9:	0f b6 9c 24 a8 00 00 	movzbl 0xa8(%rsp),%ebx
 13c2900:	00 
 13c2901:	48 8b bc 24 90 00 00 	mov    0x90(%rsp),%rdi
 13c2908:	00 
 13c2909:	48 0f af fa          	imul   %rdx,%rdi
 13c290d:	f6 84 24 98 00 00 00 	testb  $0x1,0x98(%rsp)
 13c2914:	01 
 13c2915:	0f 84 7f 01 00 00    	je     13c2a9a <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0x1ca>
 13c291b:	f6 c3 01             	test   $0x1,%bl
 13c291e:	0f 84 a6 04 00 00    	je     13c2dca <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0x4fa>
 13c2924:	49 8b 5e 10          	mov    0x10(%r14),%rbx
 13c2928:	49 39 db             	cmp    %rbx,%r11
 13c292b:	0f 83 ed 0d 00 00    	jae    13c371e <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0xe4e>
 13c2931:	49 39 da             	cmp    %rbx,%r10
 13c2934:	0f 83 f7 0d 00 00    	jae    13c3731 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0xe61>
 13c293a:	4d 8b 76 08          	mov    0x8(%r14),%r14
 13c293e:	49 c1 e3 04          	shl    $0x4,%r11
 13c2942:	4b 8d 14 1e          	lea    (%r14,%r11,1),%rdx
 13c2946:	49 c1 e2 04          	shl    $0x4,%r10
 13c294a:	4b 8d 1c 16          	lea    (%r14,%r10,1),%rbx
 13c294e:	41 80 39 00          	cmpb   $0x0,(%r9)
 13c2952:	0f 84 ac 09 00 00    	je     13c3304 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0xa34>
 13c2958:	4d 8b 41 08          	mov    0x8(%r9),%r8
 13c295c:	49 8b 49 10          	mov    0x10(%r9),%rcx
 13c2960:	49 39 c8             	cmp    %rcx,%r8
 13c2963:	0f 83 d6 09 00 00    	jae    13c333f <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0xa6f>
 13c2969:	4d 89 c7             	mov    %r8,%r15
 13c296c:	49 f7 d7             	not    %r15
 13c296f:	49 01 cf             	add    %rcx,%r15
 13c2972:	4d 8d 24 38          	lea    (%r8,%rdi,1),%r12
 13c2976:	45 31 c9             	xor    %r9d,%r9d
 13c2979:	49 89 f5             	mov    %rsi,%r13
 13c297c:	4d 29 e5             	sub    %r12,%r13
 13c297f:	4d 0f 43 cd          	cmovae %r13,%r9
 13c2983:	4d 39 cf             	cmp    %r9,%r15
 13c2986:	4d 0f 42 cf          	cmovb  %r15,%r9
 13c298a:	49 83 f9 0f          	cmp    $0xf,%r9
 13c298e:	0f 86 bf 00 00 00    	jbe    13c2a53 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0x183>
 13c2994:	4d 89 e5             	mov    %r12,%r13
 13c2997:	49 c1 e5 04          	shl    $0x4,%r13
 13c299b:	49 01 c5             	add    %rax,%r13
 13c299e:	31 ed                	xor    %ebp,%ebp
 13c29a0:	48 89 74 24 08       	mov    %rsi,0x8(%rsp)
 13c29a5:	4c 29 e6             	sub    %r12,%rsi
 13c29a8:	48 0f 43 ee          	cmovae %rsi,%rbp
 13c29ac:	49 39 ef             	cmp    %rbp,%r15
 13c29af:	49 0f 42 ef          	cmovb  %r15,%rbp
 13c29b3:	4c 01 e5             	add    %r12,%rbp
 13c29b6:	48 c1 e5 04          	shl    $0x4,%rbp
 13c29ba:	48 8d 34 28          	lea    (%rax,%rbp,1),%rsi
 13c29be:	48 83 c6 10          	add    $0x10,%rsi
 13c29c2:	4d 01 f2             	add    %r14,%r10
 13c29c5:	49 83 c2 10          	add    $0x10,%r10
 13c29c9:	4d 01 f3             	add    %r14,%r11
 13c29cc:	49 83 c3 10          	add    $0x10,%r11
 13c29d0:	4d 39 d5             	cmp    %r10,%r13
 13c29d3:	40 0f 92 c5          	setb   %bpl
 13c29d7:	48 39 f3             	cmp    %rsi,%rbx
 13c29da:	41 0f 92 c6          	setb   %r14b
 13c29de:	4d 39 dd             	cmp    %r11,%r13
 13c29e1:	41 0f 92 c2          	setb   %r10b
 13c29e5:	48 39 f2             	cmp    %rsi,%rdx
 13c29e8:	41 0f 92 c3          	setb   %r11b
 13c29ec:	44 84 f5             	test   %r14b,%bpl
 13c29ef:	75 5d                	jne    13c2a4e <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0x17e>
 13c29f1:	45 20 da             	and    %r11b,%r10b
 13c29f4:	75 58                	jne    13c2a4e <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0x17e>
 13c29f6:	48 be fe ff ff ff ff 	movabs $0x7fffffffffffffe,%rsi
 13c29fd:	ff ff 07 
 13c2a00:	49 21 f1             	and    %rsi,%r9
 13c2a03:	4f 8d 14 08          	lea    (%r8,%r9,1),%r10
 13c2a07:	49 c1 e0 04          	shl    $0x4,%r8
 13c2a0b:	49 01 c0             	add    %rax,%r8
 13c2a0e:	49 89 fb             	mov    %rdi,%r11
 13c2a11:	49 c1 e3 04          	shl    $0x4,%r11
 13c2a15:	4d 01 c3             	add    %r8,%r11
 13c2a18:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
 13c2a1f:	00 
 13c2a20:	f2 0f 10 42 08       	movsd  0x8(%rdx),%xmm0
 13c2a25:	f2 0f 58 43 08       	addsd  0x8(%rbx),%xmm0
 13c2a2a:	f2 0f 10 0a          	movsd  (%rdx),%xmm1
 13c2a2e:	f2 0f 58 0b          	addsd  (%rbx),%xmm1
 13c2a32:	66 0f 14 c8          	unpcklpd %xmm0,%xmm1
 13c2a36:	66 41 0f 11 4b 10    	movupd %xmm1,0x10(%r11)
 13c2a3c:	66 41 0f 11 0b       	movupd %xmm1,(%r11)
 13c2a41:	49 83 c3 20          	add    $0x20,%r11
 13c2a45:	49 83 c1 fe          	add    $0xfffffffffffffffe,%r9
 13c2a49:	75 d5                	jne    13c2a20 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0x150>
 13c2a4b:	4d 89 d0             	mov    %r10,%r8
 13c2a4e:	48 8b 74 24 08       	mov    0x8(%rsp),%rsi
 13c2a53:	4c 29 c1             	sub    %r8,%rcx
 13c2a56:	4c 01 c7             	add    %r8,%rdi
 13c2a59:	49 89 f8             	mov    %rdi,%r8
 13c2a5c:	49 c1 e0 04          	shl    $0x4,%r8
 13c2a60:	4c 01 c0             	add    %r8,%rax
 13c2a63:	66 66 66 66 2e 0f 1f 	data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
 13c2a6a:	84 00 00 00 00 00 
 13c2a70:	48 39 f7             	cmp    %rsi,%rdi
 13c2a73:	0f 83 2e 0c 00 00    	jae    13c36a7 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0xdd7>
 13c2a79:	66 0f 10 02          	movupd (%rdx),%xmm0
 13c2a7d:	66 0f 10 0b          	movupd (%rbx),%xmm1
 13c2a81:	66 0f 58 c8          	addpd  %xmm0,%xmm1
 13c2a85:	66 0f 11 08          	movupd %xmm1,(%rax)
 13c2a89:	48 ff c7             	inc    %rdi
 13c2a8c:	48 83 c0 10          	add    $0x10,%rax
 13c2a90:	48 ff c9             	dec    %rcx
 13c2a93:	75 db                	jne    13c2a70 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0x1a0>
 13c2a95:	e9 a5 08 00 00       	jmp    13c333f <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0xa6f>
 13c2a9a:	4c 0f af da          	imul   %rdx,%r11
 13c2a9e:	f6 c3 01             	test   $0x1,%bl
 13c2aa1:	0f 84 53 06 00 00    	je     13c30fa <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0x82a>
 13c2aa7:	49 8b 5e 10          	mov    0x10(%r14),%rbx
 13c2aab:	49 39 da             	cmp    %rbx,%r10
 13c2aae:	0f 83 7d 0c 00 00    	jae    13c3731 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0xe61>
 13c2ab4:	49 8b 5e 08          	mov    0x8(%r14),%rbx
 13c2ab8:	49 c1 e2 04          	shl    $0x4,%r10
 13c2abc:	4a 8d 14 13          	lea    (%rbx,%r10,1),%rdx
 13c2ac0:	41 80 39 00          	cmpb   $0x0,(%r9)
 13c2ac4:	0f 84 7f 07 00 00    	je     13c3249 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0x979>
 13c2aca:	4d 8b 41 08          	mov    0x8(%r9),%r8
 13c2ace:	49 8b 49 10          	mov    0x10(%r9),%rcx
 13c2ad2:	49 39 c8             	cmp    %rcx,%r8
 13c2ad5:	0f 83 64 08 00 00    	jae    13c333f <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0xa6f>
 13c2adb:	4d 89 c7             	mov    %r8,%r15
 13c2ade:	49 f7 d7             	not    %r15
 13c2ae1:	49 01 cf             	add    %rcx,%r15
 13c2ae4:	4d 8d 24 38          	lea    (%r8,%rdi,1),%r12
 13c2ae8:	45 31 f6             	xor    %r14d,%r14d
 13c2aeb:	49 89 f5             	mov    %rsi,%r13
 13c2aee:	4d 29 e5             	sub    %r12,%r13
 13c2af1:	4d 0f 42 ee          	cmovb  %r14,%r13
 13c2af5:	4d 39 ef             	cmp    %r13,%r15
 13c2af8:	4d 0f 42 ef          	cmovb  %r15,%r13
 13c2afc:	4b 8d 2c 18          	lea    (%r8,%r11,1),%rbp
 13c2b00:	49 89 f1             	mov    %rsi,%r9
 13c2b03:	48 89 6c 24 08       	mov    %rbp,0x8(%rsp)
 13c2b08:	49 29 e9             	sub    %rbp,%r9
 13c2b0b:	4d 0f 42 ce          	cmovb  %r14,%r9
 13c2b0f:	4d 39 cd             	cmp    %r9,%r13
 13c2b12:	4d 0f 42 cd          	cmovb  %r13,%r9
 13c2b16:	49 83 f9 33          	cmp    $0x33,%r9
 13c2b1a:	0f 86 53 02 00 00    	jbe    13c2d73 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0x4a3>
 13c2b20:	45 31 f6             	xor    %r14d,%r14d
 13c2b23:	49 89 f5             	mov    %rsi,%r13
 13c2b26:	4c 89 64 24 18       	mov    %r12,0x18(%rsp)
 13c2b2b:	4d 29 e5             	sub    %r12,%r13
 13c2b2e:	4d 0f 42 ee          	cmovb  %r14,%r13
 13c2b32:	4d 39 ef             	cmp    %r13,%r15
 13c2b35:	4d 0f 42 ef          	cmovb  %r15,%r13
 13c2b39:	48 89 f5             	mov    %rsi,%rbp
 13c2b3c:	4c 8b 64 24 08       	mov    0x8(%rsp),%r12
 13c2b41:	4c 29 e5             	sub    %r12,%rbp
 13c2b44:	49 0f 42 ee          	cmovb  %r14,%rbp
 13c2b48:	49 39 ed             	cmp    %rbp,%r13
 13c2b4b:	49 0f 42 ed          	cmovb  %r13,%rbp
 13c2b4f:	4d 89 e5             	mov    %r12,%r13
 13c2b52:	49 c1 e5 04          	shl    $0x4,%r13
 13c2b56:	4e 8d 34 28          	lea    (%rax,%r13,1),%r14
 13c2b5a:	4e 8d 24 28          	lea    (%rax,%r13,1),%r12
 13c2b5e:	49 83 c4 08          	add    $0x8,%r12
 13c2b62:	48 c1 e5 04          	shl    $0x4,%rbp
 13c2b66:	4c 01 f5             	add    %r14,%rbp
 13c2b69:	48 83 c5 08          	add    $0x8,%rbp
 13c2b6d:	4c 39 e5             	cmp    %r12,%rbp
 13c2b70:	0f 82 fd 01 00 00    	jb     13c2d73 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0x4a3>
 13c2b76:	4c 8d 6a 08          	lea    0x8(%rdx),%r13
 13c2b7a:	4c 89 6c 24 20       	mov    %r13,0x20(%rsp)
 13c2b7f:	48 8b 6c 24 18       	mov    0x18(%rsp),%rbp
 13c2b84:	49 89 ed             	mov    %rbp,%r13
 13c2b87:	49 c1 e5 04          	shl    $0x4,%r13
 13c2b8b:	4c 89 74 24 48       	mov    %r14,0x48(%rsp)
 13c2b90:	49 89 f6             	mov    %rsi,%r14
 13c2b93:	49 29 ee             	sub    %rbp,%r14
 13c2b96:	bd 00 00 00 00       	mov    $0x0,%ebp
 13c2b9b:	4c 0f 42 f5          	cmovb  %rbp,%r14
 13c2b9f:	4a 8d 2c 28          	lea    (%rax,%r13,1),%rbp
 13c2ba3:	48 89 6c 24 30       	mov    %rbp,0x30(%rsp)
 13c2ba8:	4d 39 f7             	cmp    %r14,%r15
 13c2bab:	4d 0f 42 f7          	cmovb  %r15,%r14
 13c2baf:	4c 89 64 24 18       	mov    %r12,0x18(%rsp)
 13c2bb4:	49 89 f4             	mov    %rsi,%r12
 13c2bb7:	4c 2b 64 24 08       	sub    0x8(%rsp),%r12
 13c2bbc:	41 bf 00 00 00 00    	mov    $0x0,%r15d
 13c2bc2:	4d 0f 42 e7          	cmovb  %r15,%r12
 13c2bc6:	4d 39 e6             	cmp    %r12,%r14
 13c2bc9:	4d 0f 42 e6          	cmovb  %r14,%r12
 13c2bcd:	49 c1 e4 04          	shl    $0x4,%r12
 13c2bd1:	4f 8d 3c 2c          	lea    (%r12,%r13,1),%r15
 13c2bd5:	4e 8d 34 38          	lea    (%rax,%r15,1),%r14
 13c2bd9:	49 83 c6 08          	add    $0x8,%r14
 13c2bdd:	4e 8d 6c 28 08       	lea    0x8(%rax,%r13,1),%r13
 13c2be2:	4e 8d 7c 38 10       	lea    0x10(%rax,%r15,1),%r15
 13c2be7:	4c 89 7c 24 50       	mov    %r15,0x50(%rsp)
 13c2bec:	4c 8b 7c 24 48       	mov    0x48(%rsp),%r15
 13c2bf1:	4b 8d 6c 3c 10       	lea    0x10(%r12,%r15,1),%rbp
 13c2bf6:	48 89 6c 24 08       	mov    %rbp,0x8(%rsp)
 13c2bfb:	4a 8d 6c 13 10       	lea    0x10(%rbx,%r10,1),%rbp
 13c2c00:	48 89 6c 24 28       	mov    %rbp,0x28(%rsp)
 13c2c05:	4c 89 fb             	mov    %r15,%rbx
 13c2c08:	4d 01 fc             	add    %r15,%r12
 13c2c0b:	49 83 c4 08          	add    $0x8,%r12
 13c2c0f:	4c 8b 54 24 30       	mov    0x30(%rsp),%r10
 13c2c14:	4c 8b 7c 24 50       	mov    0x50(%rsp),%r15
 13c2c19:	4d 39 fa             	cmp    %r15,%r10
 13c2c1c:	0f 92 44 24 40       	setb   0x40(%rsp)
 13c2c21:	4d 39 f5             	cmp    %r14,%r13
 13c2c24:	0f 92 44 24 38       	setb   0x38(%rsp)
 13c2c29:	4c 3b 54 24 08       	cmp    0x8(%rsp),%r10
 13c2c2e:	0f 92 44 24 06       	setb   0x6(%rsp)
 13c2c33:	4c 39 74 24 18       	cmp    %r14,0x18(%rsp)
 13c2c38:	0f 92 44 24 05       	setb   0x5(%rsp)
 13c2c3d:	49 39 ea             	cmp    %rbp,%r10
 13c2c40:	0f 92 44 24 04       	setb   0x4(%rsp)
 13c2c45:	48 8b 6c 24 20       	mov    0x20(%rsp),%rbp
 13c2c4a:	4c 39 f5             	cmp    %r14,%rbp
 13c2c4d:	0f 92 44 24 03       	setb   0x3(%rsp)
 13c2c52:	4d 39 e2             	cmp    %r12,%r10
 13c2c55:	0f 92 44 24 02       	setb   0x2(%rsp)
 13c2c5a:	4c 39 f3             	cmp    %r14,%rbx
 13c2c5d:	0f 92 44 24 01       	setb   0x1(%rsp)
 13c2c62:	49 39 ea             	cmp    %rbp,%r10
 13c2c65:	0f 92 44 24 30       	setb   0x30(%rsp)
 13c2c6a:	4c 39 f2             	cmp    %r14,%rdx
 13c2c6d:	0f 92 44 24 07       	setb   0x7(%rsp)
 13c2c72:	4c 3b 6c 24 08       	cmp    0x8(%rsp),%r13
 13c2c77:	0f 92 44 24 08       	setb   0x8(%rsp)
 13c2c7c:	4c 39 7c 24 18       	cmp    %r15,0x18(%rsp)
 13c2c81:	0f 92 44 24 18       	setb   0x18(%rsp)
 13c2c86:	4c 3b 6c 24 28       	cmp    0x28(%rsp),%r13
 13c2c8b:	41 0f 92 c2          	setb   %r10b
 13c2c8f:	49 89 ee             	mov    %rbp,%r14
 13c2c92:	4c 39 fd             	cmp    %r15,%rbp
 13c2c95:	0f 92 44 24 28       	setb   0x28(%rsp)
 13c2c9a:	4d 39 e5             	cmp    %r12,%r13
 13c2c9d:	40 0f 92 c5          	setb   %bpl
 13c2ca1:	4c 39 fb             	cmp    %r15,%rbx
 13c2ca4:	41 0f 92 c4          	setb   %r12b
 13c2ca8:	4d 39 f5             	cmp    %r14,%r13
 13c2cab:	41 0f 92 c6          	setb   %r14b
 13c2caf:	4c 39 fa             	cmp    %r15,%rdx
 13c2cb2:	41 0f 92 c7          	setb   %r15b
 13c2cb6:	0f b6 5c 24 38       	movzbl 0x38(%rsp),%ebx
 13c2cbb:	84 5c 24 40          	test   %bl,0x40(%rsp)
 13c2cbf:	0f 85 ae 00 00 00    	jne    13c2d73 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0x4a3>
 13c2cc5:	0f b6 5c 24 05       	movzbl 0x5(%rsp),%ebx
 13c2cca:	20 5c 24 06          	and    %bl,0x6(%rsp)
 13c2cce:	0f 85 9f 00 00 00    	jne    13c2d73 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0x4a3>
 13c2cd4:	0f b6 5c 24 03       	movzbl 0x3(%rsp),%ebx
 13c2cd9:	20 5c 24 04          	and    %bl,0x4(%rsp)
 13c2cdd:	0f 85 90 00 00 00    	jne    13c2d73 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0x4a3>
 13c2ce3:	0f b6 5c 24 01       	movzbl 0x1(%rsp),%ebx
 13c2ce8:	20 5c 24 02          	and    %bl,0x2(%rsp)
 13c2cec:	0f 85 81 00 00 00    	jne    13c2d73 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0x4a3>
 13c2cf2:	0f b6 5c 24 07       	movzbl 0x7(%rsp),%ebx
 13c2cf7:	20 5c 24 30          	and    %bl,0x30(%rsp)
 13c2cfb:	75 76                	jne    13c2d73 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0x4a3>
 13c2cfd:	0f b6 5c 24 18       	movzbl 0x18(%rsp),%ebx
 13c2d02:	20 5c 24 08          	and    %bl,0x8(%rsp)
 13c2d06:	75 6b                	jne    13c2d73 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0x4a3>
 13c2d08:	44 22 54 24 28       	and    0x28(%rsp),%r10b
 13c2d0d:	75 64                	jne    13c2d73 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0x4a3>
 13c2d0f:	44 20 e5             	and    %r12b,%bpl
 13c2d12:	75 5f                	jne    13c2d73 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0x4a3>
 13c2d14:	45 20 fe             	and    %r15b,%r14b
 13c2d17:	75 5a                	jne    13c2d73 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0x4a3>
 13c2d19:	49 ba fe ff ff ff ff 	movabs $0x7fffffffffffffe,%r10
 13c2d20:	ff ff 07 
 13c2d23:	4d 21 d1             	and    %r10,%r9
 13c2d26:	4f 8d 14 08          	lea    (%r8,%r9,1),%r10
 13c2d2a:	48 89 fb             	mov    %rdi,%rbx
 13c2d2d:	48 c1 e3 04          	shl    $0x4,%rbx
 13c2d31:	49 c1 e0 04          	shl    $0x4,%r8
 13c2d35:	49 01 c0             	add    %rax,%r8
 13c2d38:	4d 89 de             	mov    %r11,%r14
 13c2d3b:	49 c1 e6 04          	shl    $0x4,%r14
 13c2d3f:	90                   	nop
 13c2d40:	66 43 0f 10 04 30    	movupd (%r8,%r14,1),%xmm0
 13c2d46:	66 43 0f 10 4c 30 10 	movupd 0x10(%r8,%r14,1),%xmm1
 13c2d4d:	66 0f 10 12          	movupd (%rdx),%xmm2
 13c2d51:	66 0f 58 ca          	addpd  %xmm2,%xmm1
 13c2d55:	66 0f 58 c2          	addpd  %xmm2,%xmm0
 13c2d59:	66 41 0f 11 04 18    	movupd %xmm0,(%r8,%rbx,1)
 13c2d5f:	66 41 0f 11 4c 18 10 	movupd %xmm1,0x10(%r8,%rbx,1)
 13c2d66:	49 83 c0 20          	add    $0x20,%r8
 13c2d6a:	49 83 c1 fe          	add    $0xfffffffffffffffe,%r9
 13c2d6e:	75 d0                	jne    13c2d40 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0x470>
 13c2d70:	4d 89 d0             	mov    %r10,%r8
 13c2d73:	4c 01 c7             	add    %r8,%rdi
 13c2d76:	49 89 f9             	mov    %rdi,%r9
 13c2d79:	49 c1 e1 04          	shl    $0x4,%r9
 13c2d7d:	4d 01 c3             	add    %r8,%r11
 13c2d80:	4d 89 da             	mov    %r11,%r10
 13c2d83:	49 c1 e2 04          	shl    $0x4,%r10
 13c2d87:	4c 29 c1             	sub    %r8,%rcx
 13c2d8a:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
 13c2d90:	49 39 f3             	cmp    %rsi,%r11
 13c2d93:	0f 83 35 09 00 00    	jae    13c36ce <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0xdfe>
 13c2d99:	48 39 f7             	cmp    %rsi,%rdi
 13c2d9c:	0f 83 12 09 00 00    	jae    13c36b4 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0xde4>
 13c2da2:	66 42 0f 10 04 10    	movupd (%rax,%r10,1),%xmm0
 13c2da8:	66 0f 10 0a          	movupd (%rdx),%xmm1
 13c2dac:	66 0f 58 c8          	addpd  %xmm0,%xmm1
 13c2db0:	66 42 0f 11 0c 08    	movupd %xmm1,(%rax,%r9,1)
 13c2db6:	48 ff c7             	inc    %rdi
 13c2db9:	48 83 c0 10          	add    $0x10,%rax
 13c2dbd:	49 ff c3             	inc    %r11
 13c2dc0:	48 ff c9             	dec    %rcx
 13c2dc3:	75 cb                	jne    13c2d90 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0x4c0>
 13c2dc5:	e9 75 05 00 00       	jmp    13c333f <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0xa6f>
 13c2dca:	49 8b 5e 10          	mov    0x10(%r14),%rbx
 13c2dce:	49 39 db             	cmp    %rbx,%r11
 13c2dd1:	0f 83 47 09 00 00    	jae    13c371e <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0xe4e>
 13c2dd7:	4d 8b 76 08          	mov    0x8(%r14),%r14
 13c2ddb:	49 c1 e3 04          	shl    $0x4,%r11
 13c2ddf:	4b 8d 1c 1e          	lea    (%r14,%r11,1),%rbx
 13c2de3:	4c 0f af d2          	imul   %rdx,%r10
 13c2de7:	41 80 39 00          	cmpb   $0x0,(%r9)
 13c2deb:	0f 84 b6 04 00 00    	je     13c32a7 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0x9d7>
 13c2df1:	49 8b 51 08          	mov    0x8(%r9),%rdx
 13c2df5:	49 8b 49 10          	mov    0x10(%r9),%rcx
 13c2df9:	48 39 ca             	cmp    %rcx,%rdx
 13c2dfc:	0f 83 3d 05 00 00    	jae    13c333f <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0xa6f>
 13c2e02:	49 89 d4             	mov    %rdx,%r12
 13c2e05:	49 f7 d4             	not    %r12
 13c2e08:	49 01 cc             	add    %rcx,%r12
 13c2e0b:	4c 8d 3c 3a          	lea    (%rdx,%rdi,1),%r15
 13c2e0f:	45 31 c9             	xor    %r9d,%r9d
 13c2e12:	49 89 f5             	mov    %rsi,%r13
 13c2e15:	4d 29 fd             	sub    %r15,%r13
 13c2e18:	4d 0f 42 e9          	cmovb  %r9,%r13
 13c2e1c:	4d 39 ec             	cmp    %r13,%r12
 13c2e1f:	4d 0f 42 ec          	cmovb  %r12,%r13
 13c2e23:	4a 8d 2c 12          	lea    (%rdx,%r10,1),%rbp
 13c2e27:	49 89 f0             	mov    %rsi,%r8
 13c2e2a:	49 29 e8             	sub    %rbp,%r8
 13c2e2d:	4d 0f 42 c1          	cmovb  %r9,%r8
 13c2e31:	4d 39 c5             	cmp    %r8,%r13
 13c2e34:	4d 0f 42 c5          	cmovb  %r13,%r8
 13c2e38:	49 83 f8 33          	cmp    $0x33,%r8
 13c2e3c:	0f 86 61 02 00 00    	jbe    13c30a3 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0x7d3>
 13c2e42:	45 31 c9             	xor    %r9d,%r9d
 13c2e45:	49 89 f5             	mov    %rsi,%r13
 13c2e48:	4c 89 7c 24 20       	mov    %r15,0x20(%rsp)
 13c2e4d:	4d 29 fd             	sub    %r15,%r13
 13c2e50:	4d 0f 42 e9          	cmovb  %r9,%r13
 13c2e54:	45 31 ff             	xor    %r15d,%r15d
 13c2e57:	4d 39 ec             	cmp    %r13,%r12
 13c2e5a:	4d 0f 42 ec          	cmovb  %r12,%r13
 13c2e5e:	49 89 f1             	mov    %rsi,%r9
 13c2e61:	49 29 e9             	sub    %rbp,%r9
 13c2e64:	4d 0f 42 cf          	cmovb  %r15,%r9
 13c2e68:	4d 39 cd             	cmp    %r9,%r13
 13c2e6b:	4d 0f 42 cd          	cmovb  %r13,%r9
 13c2e6f:	48 89 6c 24 40       	mov    %rbp,0x40(%rsp)
 13c2e74:	49 89 ed             	mov    %rbp,%r13
 13c2e77:	49 c1 e5 04          	shl    $0x4,%r13
 13c2e7b:	4a 8d 2c 28          	lea    (%rax,%r13,1),%rbp
 13c2e7f:	4e 8d 3c 28          	lea    (%rax,%r13,1),%r15
 13c2e83:	49 83 c7 08          	add    $0x8,%r15
 13c2e87:	49 c1 e1 04          	shl    $0x4,%r9
 13c2e8b:	48 89 6c 24 08       	mov    %rbp,0x8(%rsp)
 13c2e90:	49 01 e9             	add    %rbp,%r9
 13c2e93:	49 83 c1 08          	add    $0x8,%r9
 13c2e97:	4c 89 7c 24 18       	mov    %r15,0x18(%rsp)
 13c2e9c:	4d 39 f9             	cmp    %r15,%r9
 13c2e9f:	0f 82 fe 01 00 00    	jb     13c30a3 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0x7d3>
 13c2ea5:	4c 8d 4b 08          	lea    0x8(%rbx),%r9
 13c2ea9:	4c 89 4c 24 38       	mov    %r9,0x38(%rsp)
 13c2eae:	4c 8b 7c 24 20       	mov    0x20(%rsp),%r15
 13c2eb3:	4d 89 f9             	mov    %r15,%r9
 13c2eb6:	49 c1 e1 04          	shl    $0x4,%r9
 13c2eba:	4c 89 4c 24 48       	mov    %r9,0x48(%rsp)
 13c2ebf:	49 01 c1             	add    %rax,%r9
 13c2ec2:	4c 89 4c 24 30       	mov    %r9,0x30(%rsp)
 13c2ec7:	31 ed                	xor    %ebp,%ebp
 13c2ec9:	49 89 f1             	mov    %rsi,%r9
 13c2ecc:	4d 29 f9             	sub    %r15,%r9
 13c2ecf:	4c 0f 42 cd          	cmovb  %rbp,%r9
 13c2ed3:	45 31 ff             	xor    %r15d,%r15d
 13c2ed6:	4d 39 cc             	cmp    %r9,%r12
 13c2ed9:	4d 0f 42 cc          	cmovb  %r12,%r9
 13c2edd:	48 89 f5             	mov    %rsi,%rbp
 13c2ee0:	48 2b 6c 24 40       	sub    0x40(%rsp),%rbp
 13c2ee5:	49 0f 42 ef          	cmovb  %r15,%rbp
 13c2ee9:	49 39 e9             	cmp    %rbp,%r9
 13c2eec:	49 0f 42 e9          	cmovb  %r9,%rbp
 13c2ef0:	48 c1 e5 04          	shl    $0x4,%rbp
 13c2ef4:	4c 8b 7c 24 48       	mov    0x48(%rsp),%r15
 13c2ef9:	4d 8d 24 2f          	lea    (%r15,%rbp,1),%r12
 13c2efd:	4e 8d 0c 20          	lea    (%rax,%r12,1),%r9
 13c2f01:	49 83 c1 08          	add    $0x8,%r9
 13c2f05:	4e 8d 7c 38 08       	lea    0x8(%rax,%r15,1),%r15
 13c2f0a:	49 01 c4             	add    %rax,%r12
 13c2f0d:	49 83 c4 10          	add    $0x10,%r12
 13c2f11:	4d 01 f3             	add    %r14,%r11
 13c2f14:	49 83 c3 10          	add    $0x10,%r11
 13c2f18:	4c 89 5c 24 20       	mov    %r11,0x20(%rsp)
 13c2f1d:	4c 01 ed             	add    %r13,%rbp
 13c2f20:	4c 8d 1c 28          	lea    (%rax,%rbp,1),%r11
 13c2f24:	49 83 c3 10          	add    $0x10,%r11
 13c2f28:	4c 89 5c 24 28       	mov    %r11,0x28(%rsp)
 13c2f2d:	4c 8d 2c 28          	lea    (%rax,%rbp,1),%r13
 13c2f31:	49 83 c5 08          	add    $0x8,%r13
 13c2f35:	4c 8b 74 24 30       	mov    0x30(%rsp),%r14
 13c2f3a:	4d 39 e6             	cmp    %r12,%r14
 13c2f3d:	0f 92 44 24 40       	setb   0x40(%rsp)
 13c2f42:	4d 39 cf             	cmp    %r9,%r15
 13c2f45:	0f 92 44 24 48       	setb   0x48(%rsp)
 13c2f4a:	4c 3b 74 24 20       	cmp    0x20(%rsp),%r14
 13c2f4f:	0f 92 44 24 50       	setb   0x50(%rsp)
 13c2f54:	48 8b 6c 24 38       	mov    0x38(%rsp),%rbp
 13c2f59:	4c 39 cd             	cmp    %r9,%rbp
 13c2f5c:	0f 92 44 24 06       	setb   0x6(%rsp)
 13c2f61:	4d 39 de             	cmp    %r11,%r14
 13c2f64:	0f 92 44 24 05       	setb   0x5(%rsp)
 13c2f69:	4c 8b 5c 24 18       	mov    0x18(%rsp),%r11
 13c2f6e:	4d 39 cb             	cmp    %r9,%r11
 13c2f71:	0f 92 44 24 04       	setb   0x4(%rsp)
 13c2f76:	49 39 ee             	cmp    %rbp,%r14
 13c2f79:	0f 92 44 24 03       	setb   0x3(%rsp)
 13c2f7e:	4c 39 cb             	cmp    %r9,%rbx
 13c2f81:	0f 92 44 24 02       	setb   0x2(%rsp)
 13c2f86:	4d 39 ee             	cmp    %r13,%r14
 13c2f89:	0f 92 44 24 30       	setb   0x30(%rsp)
 13c2f8e:	4c 8b 74 24 08       	mov    0x8(%rsp),%r14
 13c2f93:	4d 39 ce             	cmp    %r9,%r14
 13c2f96:	0f 92 44 24 01       	setb   0x1(%rsp)
 13c2f9b:	4c 3b 7c 24 20       	cmp    0x20(%rsp),%r15
 13c2fa0:	41 0f 92 c1          	setb   %r9b
 13c2fa4:	4c 39 e5             	cmp    %r12,%rbp
 13c2fa7:	0f 92 44 24 20       	setb   0x20(%rsp)
 13c2fac:	4c 3b 7c 24 28       	cmp    0x28(%rsp),%r15
 13c2fb1:	0f 92 44 24 28       	setb   0x28(%rsp)
 13c2fb6:	4d 39 e3             	cmp    %r12,%r11
 13c2fb9:	0f 92 44 24 18       	setb   0x18(%rsp)
 13c2fbe:	49 39 ef             	cmp    %rbp,%r15
 13c2fc1:	41 0f 92 c3          	setb   %r11b
 13c2fc5:	4c 39 e3             	cmp    %r12,%rbx
 13c2fc8:	0f 92 44 24 38       	setb   0x38(%rsp)
 13c2fcd:	4d 39 ef             	cmp    %r13,%r15
 13c2fd0:	41 0f 92 c7          	setb   %r15b
 13c2fd4:	4d 39 e6             	cmp    %r12,%r14
 13c2fd7:	41 0f 92 c4          	setb   %r12b
 13c2fdb:	0f b6 6c 24 48       	movzbl 0x48(%rsp),%ebp
 13c2fe0:	40 84 6c 24 40       	test   %bpl,0x40(%rsp)
 13c2fe5:	0f 85 b8 00 00 00    	jne    13c30a3 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0x7d3>
 13c2feb:	0f b6 6c 24 06       	movzbl 0x6(%rsp),%ebp
 13c2ff0:	40 20 6c 24 50       	and    %bpl,0x50(%rsp)
 13c2ff5:	0f 85 a8 00 00 00    	jne    13c30a3 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0x7d3>
 13c2ffb:	0f b6 6c 24 04       	movzbl 0x4(%rsp),%ebp
 13c3000:	40 20 6c 24 05       	and    %bpl,0x5(%rsp)
 13c3005:	0f 85 98 00 00 00    	jne    13c30a3 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0x7d3>
 13c300b:	0f b6 6c 24 02       	movzbl 0x2(%rsp),%ebp
 13c3010:	40 20 6c 24 03       	and    %bpl,0x3(%rsp)
 13c3015:	0f 85 88 00 00 00    	jne    13c30a3 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0x7d3>
 13c301b:	0f b6 6c 24 01       	movzbl 0x1(%rsp),%ebp
 13c3020:	40 20 6c 24 30       	and    %bpl,0x30(%rsp)
 13c3025:	75 7c                	jne    13c30a3 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0x7d3>
 13c3027:	44 22 4c 24 20       	and    0x20(%rsp),%r9b
 13c302c:	75 75                	jne    13c30a3 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0x7d3>
 13c302e:	44 0f b6 4c 24 18    	movzbl 0x18(%rsp),%r9d
 13c3034:	44 20 4c 24 28       	and    %r9b,0x28(%rsp)
 13c3039:	75 68                	jne    13c30a3 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0x7d3>
 13c303b:	44 22 5c 24 38       	and    0x38(%rsp),%r11b
 13c3040:	75 61                	jne    13c30a3 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0x7d3>
 13c3042:	45 20 e7             	and    %r12b,%r15b
 13c3045:	75 5c                	jne    13c30a3 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0x7d3>
 13c3047:	49 b9 fe ff ff ff ff 	movabs $0x7fffffffffffffe,%r9
 13c304e:	ff ff 07 
 13c3051:	4d 21 c8             	and    %r9,%r8
 13c3054:	4e 8d 0c 02          	lea    (%rdx,%r8,1),%r9
 13c3058:	49 89 fb             	mov    %rdi,%r11
 13c305b:	49 c1 e3 04          	shl    $0x4,%r11
 13c305f:	48 c1 e2 04          	shl    $0x4,%rdx
 13c3063:	48 01 c2             	add    %rax,%rdx
 13c3066:	4d 89 d6             	mov    %r10,%r14
 13c3069:	49 c1 e6 04          	shl    $0x4,%r14
 13c306d:	0f 1f 00             	nopl   (%rax)
 13c3070:	66 42 0f 10 04 32    	movupd (%rdx,%r14,1),%xmm0
 13c3076:	66 42 0f 10 4c 32 10 	movupd 0x10(%rdx,%r14,1),%xmm1
 13c307d:	66 0f 10 13          	movupd (%rbx),%xmm2
 13c3081:	66 0f 58 c2          	addpd  %xmm2,%xmm0
 13c3085:	66 0f 58 ca          	addpd  %xmm2,%xmm1
 13c3089:	66 42 0f 11 4c 1a 10 	movupd %xmm1,0x10(%rdx,%r11,1)
 13c3090:	66 42 0f 11 04 1a    	movupd %xmm0,(%rdx,%r11,1)
 13c3096:	48 83 c2 20          	add    $0x20,%rdx
 13c309a:	49 83 c0 fe          	add    $0xfffffffffffffffe,%r8
 13c309e:	75 d0                	jne    13c3070 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0x7a0>
 13c30a0:	4c 89 ca             	mov    %r9,%rdx
 13c30a3:	48 01 d7             	add    %rdx,%rdi
 13c30a6:	49 89 f8             	mov    %rdi,%r8
 13c30a9:	49 c1 e0 04          	shl    $0x4,%r8
 13c30ad:	49 01 d2             	add    %rdx,%r10
 13c30b0:	4d 89 d1             	mov    %r10,%r9
 13c30b3:	49 c1 e1 04          	shl    $0x4,%r9
 13c30b7:	48 29 d1             	sub    %rdx,%rcx
 13c30ba:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
 13c30c0:	49 39 f2             	cmp    %rsi,%r10
 13c30c3:	0f 83 15 06 00 00    	jae    13c36de <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0xe0e>
 13c30c9:	48 39 f7             	cmp    %rsi,%rdi
 13c30cc:	0f 83 ef 05 00 00    	jae    13c36c1 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0xdf1>
 13c30d2:	66 0f 10 03          	movupd (%rbx),%xmm0
 13c30d6:	66 42 0f 10 0c 08    	movupd (%rax,%r9,1),%xmm1
 13c30dc:	66 0f 58 c8          	addpd  %xmm0,%xmm1
 13c30e0:	66 42 0f 11 0c 00    	movupd %xmm1,(%rax,%r8,1)
 13c30e6:	48 ff c7             	inc    %rdi
 13c30e9:	48 83 c0 10          	add    $0x10,%rax
 13c30ed:	49 ff c2             	inc    %r10
 13c30f0:	48 ff c9             	dec    %rcx
 13c30f3:	75 cb                	jne    13c30c0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0x7f0>
 13c30f5:	e9 45 02 00 00       	jmp    13c333f <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0xa6f>
 13c30fa:	4c 0f af d2          	imul   %rdx,%r10
 13c30fe:	41 83 39 01          	cmpl   $0x1,(%r9)
 13c3102:	0f 85 d5 00 00 00    	jne    13c31dd <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0x90d>
 13c3108:	4d 8b 41 08          	mov    0x8(%r9),%r8
 13c310c:	49 8b 51 10          	mov    0x10(%r9),%rdx
 13c3110:	49 39 d0             	cmp    %rdx,%r8
 13c3113:	0f 83 26 02 00 00    	jae    13c333f <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0xa6f>
 13c3119:	4d 89 c1             	mov    %r8,%r9
 13c311c:	49 f7 d1             	not    %r9
 13c311f:	49 01 d1             	add    %rdx,%r9
 13c3122:	4b 8d 1c 10          	lea    (%r8,%r10,1),%rbx
 13c3126:	45 31 ff             	xor    %r15d,%r15d
 13c3129:	48 89 f1             	mov    %rsi,%rcx
 13c312c:	48 29 d9             	sub    %rbx,%rcx
 13c312f:	49 0f 42 cf          	cmovb  %r15,%rcx
 13c3133:	49 39 c9             	cmp    %rcx,%r9
 13c3136:	49 0f 42 c9          	cmovb  %r9,%rcx
 13c313a:	4f 8d 34 18          	lea    (%r8,%r11,1),%r14
 13c313e:	49 89 f4             	mov    %rsi,%r12
 13c3141:	4d 29 f4             	sub    %r14,%r12
 13c3144:	4d 0f 42 e7          	cmovb  %r15,%r12
 13c3148:	4c 39 e1             	cmp    %r12,%rcx
 13c314b:	4c 0f 42 e1          	cmovb  %rcx,%r12
 13c314f:	49 8d 2c 38          	lea    (%r8,%rdi,1),%rbp
 13c3153:	48 89 f1             	mov    %rsi,%rcx
 13c3156:	48 29 e9             	sub    %rbp,%rcx
 13c3159:	49 0f 42 cf          	cmovb  %r15,%rcx
 13c315d:	49 39 cc             	cmp    %rcx,%r12
 13c3160:	49 0f 42 cc          	cmovb  %r12,%rcx
 13c3164:	48 83 f9 3b          	cmp    $0x3b,%rcx
 13c3168:	0f 87 e0 01 00 00    	ja     13c334e <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0xa7e>
 13c316e:	4d 8d 0c 38          	lea    (%r8,%rdi,1),%r9
 13c3172:	49 c1 e1 04          	shl    $0x4,%r9
 13c3176:	4b 8d 1c 10          	lea    (%r8,%r10,1),%rbx
 13c317a:	48 c1 e3 04          	shl    $0x4,%rbx
 13c317e:	4f 8d 34 18          	lea    (%r8,%r11,1),%r14
 13c3182:	49 c1 e6 04          	shl    $0x4,%r14
 13c3186:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
 13c318d:	00 00 00 
 13c3190:	4b 8d 0c 03          	lea    (%r11,%r8,1),%rcx
 13c3194:	48 39 f1             	cmp    %rsi,%rcx
 13c3197:	0f 83 71 05 00 00    	jae    13c370e <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0xe3e>
 13c319d:	4b 8d 0c 02          	lea    (%r10,%r8,1),%rcx
 13c31a1:	48 39 f1             	cmp    %rsi,%rcx
 13c31a4:	0f 83 54 05 00 00    	jae    13c36fe <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0xe2e>
 13c31aa:	4a 8d 0c 07          	lea    (%rdi,%r8,1),%rcx
 13c31ae:	48 39 f1             	cmp    %rsi,%rcx
 13c31b1:	0f 83 37 05 00 00    	jae    13c36ee <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0xe1e>
 13c31b7:	49 ff c0             	inc    %r8
 13c31ba:	66 42 0f 10 04 30    	movupd (%rax,%r14,1),%xmm0
 13c31c0:	66 0f 10 0c 18       	movupd (%rax,%rbx,1),%xmm1
 13c31c5:	66 0f 58 c8          	addpd  %xmm0,%xmm1
 13c31c9:	66 42 0f 11 0c 08    	movupd %xmm1,(%rax,%r9,1)
 13c31cf:	48 83 c0 10          	add    $0x10,%rax
 13c31d3:	4c 39 c2             	cmp    %r8,%rdx
 13c31d6:	75 b8                	jne    13c3190 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0x8c0>
 13c31d8:	e9 62 01 00 00       	jmp    13c333f <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0xa6f>
 13c31dd:	4d 85 c0             	test   %r8,%r8
 13c31e0:	0f 84 59 01 00 00    	je     13c333f <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0xa6f>
 13c31e6:	49 c1 e0 03          	shl    $0x3,%r8
 13c31ea:	31 d2                	xor    %edx,%edx
 13c31ec:	0f 1f 40 00          	nopl   0x0(%rax)
 13c31f0:	4c 8b 34 11          	mov    (%rcx,%rdx,1),%r14
 13c31f4:	4f 8d 0c 1e          	lea    (%r14,%r11,1),%r9
 13c31f8:	49 39 f1             	cmp    %rsi,%r9
 13c31fb:	0f 83 96 04 00 00    	jae    13c3697 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0xdc7>
 13c3201:	4b 8d 1c 16          	lea    (%r14,%r10,1),%rbx
 13c3205:	48 39 f3             	cmp    %rsi,%rbx
 13c3208:	0f 83 79 04 00 00    	jae    13c3687 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0xdb7>
 13c320e:	49 01 fe             	add    %rdi,%r14
 13c3211:	49 39 f6             	cmp    %rsi,%r14
 13c3214:	0f 83 5d 04 00 00    	jae    13c3677 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0xda7>
 13c321a:	49 c1 e1 04          	shl    $0x4,%r9
 13c321e:	48 c1 e3 04          	shl    $0x4,%rbx
 13c3222:	49 c1 e6 04          	shl    $0x4,%r14
 13c3226:	66 42 0f 10 04 08    	movupd (%rax,%r9,1),%xmm0
 13c322c:	66 0f 10 0c 18       	movupd (%rax,%rbx,1),%xmm1
 13c3231:	66 0f 58 c8          	addpd  %xmm0,%xmm1
 13c3235:	66 42 0f 11 0c 30    	movupd %xmm1,(%rax,%r14,1)
 13c323b:	48 83 c2 08          	add    $0x8,%rdx
 13c323f:	49 39 d0             	cmp    %rdx,%r8
 13c3242:	75 ac                	jne    13c31f0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0x920>
 13c3244:	e9 f6 00 00 00       	jmp    13c333f <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0xa6f>
 13c3249:	4d 85 c0             	test   %r8,%r8
 13c324c:	0f 84 ed 00 00 00    	je     13c333f <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0xa6f>
 13c3252:	49 c1 e0 03          	shl    $0x3,%r8
 13c3256:	31 db                	xor    %ebx,%ebx
 13c3258:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
 13c325f:	00 
 13c3260:	4c 8b 14 19          	mov    (%rcx,%rbx,1),%r10
 13c3264:	4f 8d 0c 1a          	lea    (%r10,%r11,1),%r9
 13c3268:	49 39 f1             	cmp    %rsi,%r9
 13c326b:	0f 83 e6 03 00 00    	jae    13c3657 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0xd87>
 13c3271:	49 01 fa             	add    %rdi,%r10
 13c3274:	49 39 f2             	cmp    %rsi,%r10
 13c3277:	0f 83 ba 03 00 00    	jae    13c3637 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0xd67>
 13c327d:	49 c1 e1 04          	shl    $0x4,%r9
 13c3281:	49 c1 e2 04          	shl    $0x4,%r10
 13c3285:	66 42 0f 10 04 08    	movupd (%rax,%r9,1),%xmm0
 13c328b:	66 0f 10 0a          	movupd (%rdx),%xmm1
 13c328f:	66 0f 58 c8          	addpd  %xmm0,%xmm1
 13c3293:	66 42 0f 11 0c 10    	movupd %xmm1,(%rax,%r10,1)
 13c3299:	48 83 c3 08          	add    $0x8,%rbx
 13c329d:	49 39 d8             	cmp    %rbx,%r8
 13c32a0:	75 be                	jne    13c3260 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0x990>
 13c32a2:	e9 98 00 00 00       	jmp    13c333f <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0xa6f>
 13c32a7:	4d 85 c0             	test   %r8,%r8
 13c32aa:	0f 84 8f 00 00 00    	je     13c333f <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0xa6f>
 13c32b0:	49 c1 e0 03          	shl    $0x3,%r8
 13c32b4:	31 d2                	xor    %edx,%edx
 13c32b6:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
 13c32bd:	00 00 00 
 13c32c0:	4c 8b 1c 11          	mov    (%rcx,%rdx,1),%r11
 13c32c4:	4f 8d 0c 13          	lea    (%r11,%r10,1),%r9
 13c32c8:	49 39 f1             	cmp    %rsi,%r9
 13c32cb:	0f 83 96 03 00 00    	jae    13c3667 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0xd97>
 13c32d1:	49 01 fb             	add    %rdi,%r11
 13c32d4:	49 39 f3             	cmp    %rsi,%r11
 13c32d7:	0f 83 6a 03 00 00    	jae    13c3647 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0xd77>
 13c32dd:	49 c1 e1 04          	shl    $0x4,%r9
 13c32e1:	49 c1 e3 04          	shl    $0x4,%r11
 13c32e5:	66 0f 10 03          	movupd (%rbx),%xmm0
 13c32e9:	66 42 0f 10 0c 08    	movupd (%rax,%r9,1),%xmm1
 13c32ef:	66 0f 58 c8          	addpd  %xmm0,%xmm1
 13c32f3:	66 42 0f 11 0c 18    	movupd %xmm1,(%rax,%r11,1)
 13c32f9:	48 83 c2 08          	add    $0x8,%rdx
 13c32fd:	49 39 d0             	cmp    %rdx,%r8
 13c3300:	75 be                	jne    13c32c0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0x9f0>
 13c3302:	eb 3b                	jmp    13c333f <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0xa6f>
 13c3304:	4d 85 c0             	test   %r8,%r8
 13c3307:	74 36                	je     13c333f <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0xa6f>
 13c3309:	49 c1 e0 03          	shl    $0x3,%r8
 13c330d:	45 31 d2             	xor    %r10d,%r10d
 13c3310:	4e 8b 0c 11          	mov    (%rcx,%r10,1),%r9
 13c3314:	49 01 f9             	add    %rdi,%r9
 13c3317:	49 39 f1             	cmp    %rsi,%r9
 13c331a:	0f 83 07 03 00 00    	jae    13c3627 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0xd57>
 13c3320:	49 c1 e1 04          	shl    $0x4,%r9
 13c3324:	66 0f 10 02          	movupd (%rdx),%xmm0
 13c3328:	66 0f 10 0b          	movupd (%rbx),%xmm1
 13c332c:	66 0f 58 c8          	addpd  %xmm0,%xmm1
 13c3330:	66 42 0f 11 0c 08    	movupd %xmm1,(%rax,%r9,1)
 13c3336:	49 83 c2 08          	add    $0x8,%r10
 13c333a:	4d 39 d0             	cmp    %r10,%r8
 13c333d:	75 d1                	jne    13c3310 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0xa40>
 13c333f:	48 83 c4 58          	add    $0x58,%rsp
 13c3343:	5b                   	pop    %rbx
 13c3344:	41 5c                	pop    %r12
 13c3346:	41 5d                	pop    %r13
 13c3348:	41 5e                	pop    %r14
 13c334a:	41 5f                	pop    %r15
 13c334c:	5d                   	pop    %rbp
 13c334d:	c3                   	ret
 13c334e:	45 31 e4             	xor    %r12d,%r12d
 13c3351:	49 89 f7             	mov    %rsi,%r15
 13c3354:	49 29 df             	sub    %rbx,%r15
 13c3357:	4d 0f 42 fc          	cmovb  %r12,%r15
 13c335b:	4d 39 f9             	cmp    %r15,%r9
 13c335e:	4d 0f 42 f9          	cmovb  %r9,%r15
 13c3362:	49 89 f5             	mov    %rsi,%r13
 13c3365:	4d 29 f5             	sub    %r14,%r13
 13c3368:	4d 0f 42 ec          	cmovb  %r12,%r13
 13c336c:	4d 39 ef             	cmp    %r13,%r15
 13c336f:	4d 0f 42 ef          	cmovb  %r15,%r13
 13c3373:	49 89 f7             	mov    %rsi,%r15
 13c3376:	48 89 6c 24 08       	mov    %rbp,0x8(%rsp)
 13c337b:	49 29 ef             	sub    %rbp,%r15
 13c337e:	4d 0f 42 fc          	cmovb  %r12,%r15
 13c3382:	4d 39 fd             	cmp    %r15,%r13
 13c3385:	4d 0f 42 fd          	cmovb  %r13,%r15
 13c3389:	4d 89 f5             	mov    %r14,%r13
 13c338c:	49 c1 e5 04          	shl    $0x4,%r13
 13c3390:	4e 8d 24 28          	lea    (%rax,%r13,1),%r12
 13c3394:	4a 8d 2c 28          	lea    (%rax,%r13,1),%rbp
 13c3398:	48 83 c5 08          	add    $0x8,%rbp
 13c339c:	49 c1 e7 04          	shl    $0x4,%r15
 13c33a0:	4c 89 64 24 18       	mov    %r12,0x18(%rsp)
 13c33a5:	4d 01 fc             	add    %r15,%r12
 13c33a8:	49 83 c4 08          	add    $0x8,%r12
 13c33ac:	49 39 ec             	cmp    %rbp,%r12
 13c33af:	0f 82 b9 fd ff ff    	jb     13c316e <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0x89e>
 13c33b5:	48 89 6c 24 30       	mov    %rbp,0x30(%rsp)
 13c33ba:	48 89 5c 24 20       	mov    %rbx,0x20(%rsp)
 13c33bf:	49 89 dc             	mov    %rbx,%r12
 13c33c2:	49 c1 e4 04          	shl    $0x4,%r12
 13c33c6:	4a 8d 2c 20          	lea    (%rax,%r12,1),%rbp
 13c33ca:	4a 8d 1c 20          	lea    (%rax,%r12,1),%rbx
 13c33ce:	48 83 c3 08          	add    $0x8,%rbx
 13c33d2:	48 89 6c 24 48       	mov    %rbp,0x48(%rsp)
 13c33d7:	49 01 ef             	add    %rbp,%r15
 13c33da:	49 83 c7 08          	add    $0x8,%r15
 13c33de:	48 89 5c 24 28       	mov    %rbx,0x28(%rsp)
 13c33e3:	49 39 df             	cmp    %rbx,%r15
 13c33e6:	0f 82 82 fd ff ff    	jb     13c316e <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0x89e>
 13c33ec:	4c 8b 7c 24 08       	mov    0x8(%rsp),%r15
 13c33f1:	49 c1 e7 04          	shl    $0x4,%r15
 13c33f5:	48 89 f5             	mov    %rsi,%rbp
 13c33f8:	48 2b 6c 24 20       	sub    0x20(%rsp),%rbp
 13c33fd:	bb 00 00 00 00       	mov    $0x0,%ebx
 13c3402:	48 0f 42 eb          	cmovb  %rbx,%rbp
 13c3406:	49 39 e9             	cmp    %rbp,%r9
 13c3409:	49 0f 42 e9          	cmovb  %r9,%rbp
 13c340d:	49 89 f1             	mov    %rsi,%r9
 13c3410:	4d 29 f1             	sub    %r14,%r9
 13c3413:	bb 00 00 00 00       	mov    $0x0,%ebx
 13c3418:	4c 0f 42 cb          	cmovb  %rbx,%r9
 13c341c:	31 db                	xor    %ebx,%ebx
 13c341e:	4c 39 cd             	cmp    %r9,%rbp
 13c3421:	4c 0f 42 cd          	cmovb  %rbp,%r9
 13c3425:	49 89 f6             	mov    %rsi,%r14
 13c3428:	4c 2b 74 24 08       	sub    0x8(%rsp),%r14
 13c342d:	4c 0f 42 f3          	cmovb  %rbx,%r14
 13c3431:	4d 39 f1             	cmp    %r14,%r9
 13c3434:	4d 0f 42 f1          	cmovb  %r9,%r14
 13c3438:	4a 8d 2c 38          	lea    (%rax,%r15,1),%rbp
 13c343c:	49 c1 e6 04          	shl    $0x4,%r14
 13c3440:	4b 8d 1c 3e          	lea    (%r14,%r15,1),%rbx
 13c3444:	4c 8d 0c 18          	lea    (%rax,%rbx,1),%r9
 13c3448:	49 83 c1 08          	add    $0x8,%r9
 13c344c:	49 01 c7             	add    %rax,%r15
 13c344f:	49 83 c7 08          	add    $0x8,%r15
 13c3453:	4c 89 7c 24 20       	mov    %r15,0x20(%rsp)
 13c3458:	4c 8d 3c 18          	lea    (%rax,%rbx,1),%r15
 13c345c:	49 83 c7 10          	add    $0x10,%r15
 13c3460:	49 01 c6             	add    %rax,%r14
 13c3463:	4b 8d 1c 2e          	lea    (%r14,%r13,1),%rbx
 13c3467:	48 83 c3 10          	add    $0x10,%rbx
 13c346b:	48 89 5c 24 38       	mov    %rbx,0x38(%rsp)
 13c3470:	4b 8d 5c 34 10       	lea    0x10(%r12,%r14,1),%rbx
 13c3475:	48 89 5c 24 40       	mov    %rbx,0x40(%rsp)
 13c347a:	4d 01 f5             	add    %r14,%r13
 13c347d:	49 83 c5 08          	add    $0x8,%r13
 13c3481:	4d 01 e6             	add    %r12,%r14
 13c3484:	49 83 c6 08          	add    $0x8,%r14
 13c3488:	4c 89 74 24 08       	mov    %r14,0x8(%rsp)
 13c348d:	4c 39 fd             	cmp    %r15,%rbp
 13c3490:	0f 92 44 24 50       	setb   0x50(%rsp)
 13c3495:	4c 39 4c 24 20       	cmp    %r9,0x20(%rsp)
 13c349a:	0f 92 44 24 06       	setb   0x6(%rsp)
 13c349f:	48 3b 6c 24 38       	cmp    0x38(%rsp),%rbp
 13c34a4:	0f 92 44 24 05       	setb   0x5(%rsp)
 13c34a9:	4c 8b 64 24 30       	mov    0x30(%rsp),%r12
 13c34ae:	4d 39 cc             	cmp    %r9,%r12
 13c34b1:	0f 92 44 24 04       	setb   0x4(%rsp)
 13c34b6:	48 3b 6c 24 40       	cmp    0x40(%rsp),%rbp
 13c34bb:	0f 92 44 24 03       	setb   0x3(%rsp)
 13c34c0:	48 8b 5c 24 28       	mov    0x28(%rsp),%rbx
 13c34c5:	4c 39 cb             	cmp    %r9,%rbx
 13c34c8:	0f 92 44 24 02       	setb   0x2(%rsp)
 13c34cd:	4c 39 ed             	cmp    %r13,%rbp
 13c34d0:	0f 92 44 24 01       	setb   0x1(%rsp)
 13c34d5:	4c 8b 74 24 18       	mov    0x18(%rsp),%r14
 13c34da:	4d 39 ce             	cmp    %r9,%r14
 13c34dd:	0f 92 44 24 07       	setb   0x7(%rsp)
 13c34e2:	48 3b 6c 24 08       	cmp    0x8(%rsp),%rbp
 13c34e7:	0f 92 44 24 17       	setb   0x17(%rsp)
 13c34ec:	48 8b 6c 24 48       	mov    0x48(%rsp),%rbp
 13c34f1:	4c 39 cd             	cmp    %r9,%rbp
 13c34f4:	0f 92 44 24 16       	setb   0x16(%rsp)
 13c34f9:	4c 8b 4c 24 20       	mov    0x20(%rsp),%r9
 13c34fe:	4c 3b 4c 24 38       	cmp    0x38(%rsp),%r9
 13c3503:	0f 92 44 24 38       	setb   0x38(%rsp)
 13c3508:	4d 39 fc             	cmp    %r15,%r12
 13c350b:	0f 92 44 24 30       	setb   0x30(%rsp)
 13c3510:	4c 3b 4c 24 40       	cmp    0x40(%rsp),%r9
 13c3515:	4d 89 cc             	mov    %r9,%r12
 13c3518:	41 0f 92 c1          	setb   %r9b
 13c351c:	4c 39 fb             	cmp    %r15,%rbx
 13c351f:	0f 92 44 24 40       	setb   0x40(%rsp)
 13c3524:	4d 39 ec             	cmp    %r13,%r12
 13c3527:	0f 92 44 24 28       	setb   0x28(%rsp)
 13c352c:	4d 39 fe             	cmp    %r15,%r14
 13c352f:	0f 92 44 24 18       	setb   0x18(%rsp)
 13c3534:	4c 3b 64 24 08       	cmp    0x8(%rsp),%r12
 13c3539:	0f 92 c3             	setb   %bl
 13c353c:	4c 39 fd             	cmp    %r15,%rbp
 13c353f:	40 0f 92 c5          	setb   %bpl
 13c3543:	44 0f b6 74 24 06    	movzbl 0x6(%rsp),%r14d
 13c3549:	44 84 74 24 50       	test   %r14b,0x50(%rsp)
 13c354e:	0f 85 1a fc ff ff    	jne    13c316e <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0x89e>
 13c3554:	44 0f b6 74 24 04    	movzbl 0x4(%rsp),%r14d
 13c355a:	44 20 74 24 05       	and    %r14b,0x5(%rsp)
 13c355f:	0f 85 09 fc ff ff    	jne    13c316e <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0x89e>
 13c3565:	44 0f b6 74 24 02    	movzbl 0x2(%rsp),%r14d
 13c356b:	44 20 74 24 03       	and    %r14b,0x3(%rsp)
 13c3570:	0f 85 f8 fb ff ff    	jne    13c316e <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0x89e>
 13c3576:	44 0f b6 74 24 07    	movzbl 0x7(%rsp),%r14d
 13c357c:	44 20 74 24 01       	and    %r14b,0x1(%rsp)
 13c3581:	0f 85 e7 fb ff ff    	jne    13c316e <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0x89e>
 13c3587:	44 0f b6 74 24 16    	movzbl 0x16(%rsp),%r14d
 13c358d:	44 20 74 24 17       	and    %r14b,0x17(%rsp)
 13c3592:	0f 85 d6 fb ff ff    	jne    13c316e <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0x89e>
 13c3598:	44 0f b6 74 24 30    	movzbl 0x30(%rsp),%r14d
 13c359e:	44 20 74 24 38       	and    %r14b,0x38(%rsp)
 13c35a3:	0f 85 c5 fb ff ff    	jne    13c316e <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0x89e>
 13c35a9:	44 22 4c 24 40       	and    0x40(%rsp),%r9b
 13c35ae:	0f 85 ba fb ff ff    	jne    13c316e <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0x89e>
 13c35b4:	44 0f b6 4c 24 18    	movzbl 0x18(%rsp),%r9d
 13c35ba:	44 20 4c 24 28       	and    %r9b,0x28(%rsp)
 13c35bf:	0f 85 a9 fb ff ff    	jne    13c316e <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0x89e>
 13c35c5:	40 20 eb             	and    %bpl,%bl
 13c35c8:	0f 85 a0 fb ff ff    	jne    13c316e <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0x89e>
 13c35ce:	49 b9 fe ff ff ff ff 	movabs $0x7fffffffffffffe,%r9
 13c35d5:	ff ff 07 
 13c35d8:	4c 21 c9             	and    %r9,%rcx
 13c35db:	4d 8d 0c 08          	lea    (%r8,%rcx,1),%r9
 13c35df:	48 89 fb             	mov    %rdi,%rbx
 13c35e2:	48 c1 e3 04          	shl    $0x4,%rbx
 13c35e6:	49 c1 e0 04          	shl    $0x4,%r8
 13c35ea:	49 01 c0             	add    %rax,%r8
 13c35ed:	4d 89 d6             	mov    %r10,%r14
 13c35f0:	49 c1 e6 04          	shl    $0x4,%r14
 13c35f4:	4d 89 df             	mov    %r11,%r15
 13c35f7:	49 c1 e7 04          	shl    $0x4,%r15
 13c35fb:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
 13c3600:	66 43 0f 10 04 38    	movupd (%r8,%r15,1),%xmm0
 13c3606:	66 43 0f 10 0c 30    	movupd (%r8,%r14,1),%xmm1
 13c360c:	66 0f 58 c8          	addpd  %xmm0,%xmm1
 13c3610:	66 41 0f 11 0c 18    	movupd %xmm1,(%r8,%rbx,1)
 13c3616:	49 83 c0 10          	add    $0x10,%r8
 13c361a:	48 ff c9             	dec    %rcx
 13c361d:	75 e1                	jne    13c3600 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0xd30>
 13c361f:	4d 89 c8             	mov    %r9,%r8
 13c3622:	e9 47 fb ff ff       	jmp    13c316e <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>+0x89e>
 13c3627:	48 8d 15 42 4f 4f 02 	lea    0x24f4f42(%rip),%rdx        # 38b8570 <anon.f07db1e3109bdebbfd722d22fe4a7549.2.llvm.5971120963962824495+0xd8>
 13c362e:	4c 89 cf             	mov    %r9,%rdi
 13c3631:	ff 15 99 78 58 02    	call   *0x2587899(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 13c3637:	48 8d 15 ea 4e 4f 02 	lea    0x24f4eea(%rip),%rdx        # 38b8528 <anon.f07db1e3109bdebbfd722d22fe4a7549.2.llvm.5971120963962824495+0x90>
 13c363e:	4c 89 d7             	mov    %r10,%rdi
 13c3641:	ff 15 89 78 58 02    	call   *0x2587889(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 13c3647:	48 8d 15 0a 4f 4f 02 	lea    0x24f4f0a(%rip),%rdx        # 38b8558 <anon.f07db1e3109bdebbfd722d22fe4a7549.2.llvm.5971120963962824495+0xc0>
 13c364e:	4c 89 df             	mov    %r11,%rdi
 13c3651:	ff 15 79 78 58 02    	call   *0x2587879(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 13c3657:	48 8d 15 b2 4e 4f 02 	lea    0x24f4eb2(%rip),%rdx        # 38b8510 <anon.f07db1e3109bdebbfd722d22fe4a7549.2.llvm.5971120963962824495+0x78>
 13c365e:	4c 89 cf             	mov    %r9,%rdi
 13c3661:	ff 15 69 78 58 02    	call   *0x2587869(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 13c3667:	48 8d 15 d2 4e 4f 02 	lea    0x24f4ed2(%rip),%rdx        # 38b8540 <anon.f07db1e3109bdebbfd722d22fe4a7549.2.llvm.5971120963962824495+0xa8>
 13c366e:	4c 89 cf             	mov    %r9,%rdi
 13c3671:	ff 15 59 78 58 02    	call   *0x2587859(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 13c3677:	48 8d 15 62 4e 4f 02 	lea    0x24f4e62(%rip),%rdx        # 38b84e0 <anon.f07db1e3109bdebbfd722d22fe4a7549.2.llvm.5971120963962824495+0x48>
 13c367e:	4c 89 f7             	mov    %r14,%rdi
 13c3681:	ff 15 49 78 58 02    	call   *0x2587849(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 13c3687:	48 8d 15 3a 4e 4f 02 	lea    0x24f4e3a(%rip),%rdx        # 38b84c8 <anon.f07db1e3109bdebbfd722d22fe4a7549.2.llvm.5971120963962824495+0x30>
 13c368e:	48 89 df             	mov    %rbx,%rdi
 13c3691:	ff 15 39 78 58 02    	call   *0x2587839(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 13c3697:	48 8d 15 12 4e 4f 02 	lea    0x24f4e12(%rip),%rdx        # 38b84b0 <anon.f07db1e3109bdebbfd722d22fe4a7549.2.llvm.5971120963962824495+0x18>
 13c369e:	4c 89 cf             	mov    %r9,%rdi
 13c36a1:	ff 15 29 78 58 02    	call   *0x2587829(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 13c36a7:	48 8d 15 c2 4e 4f 02 	lea    0x24f4ec2(%rip),%rdx        # 38b8570 <anon.f07db1e3109bdebbfd722d22fe4a7549.2.llvm.5971120963962824495+0xd8>
 13c36ae:	ff 15 1c 78 58 02    	call   *0x258781c(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 13c36b4:	48 8d 15 6d 4e 4f 02 	lea    0x24f4e6d(%rip),%rdx        # 38b8528 <anon.f07db1e3109bdebbfd722d22fe4a7549.2.llvm.5971120963962824495+0x90>
 13c36bb:	ff 15 0f 78 58 02    	call   *0x258780f(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 13c36c1:	48 8d 15 90 4e 4f 02 	lea    0x24f4e90(%rip),%rdx        # 38b8558 <anon.f07db1e3109bdebbfd722d22fe4a7549.2.llvm.5971120963962824495+0xc0>
 13c36c8:	ff 15 02 78 58 02    	call   *0x2587802(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 13c36ce:	48 8d 15 3b 4e 4f 02 	lea    0x24f4e3b(%rip),%rdx        # 38b8510 <anon.f07db1e3109bdebbfd722d22fe4a7549.2.llvm.5971120963962824495+0x78>
 13c36d5:	4c 89 df             	mov    %r11,%rdi
 13c36d8:	ff 15 f2 77 58 02    	call   *0x25877f2(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 13c36de:	48 8d 15 5b 4e 4f 02 	lea    0x24f4e5b(%rip),%rdx        # 38b8540 <anon.f07db1e3109bdebbfd722d22fe4a7549.2.llvm.5971120963962824495+0xa8>
 13c36e5:	4c 89 d7             	mov    %r10,%rdi
 13c36e8:	ff 15 e2 77 58 02    	call   *0x25877e2(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 13c36ee:	48 8d 15 eb 4d 4f 02 	lea    0x24f4deb(%rip),%rdx        # 38b84e0 <anon.f07db1e3109bdebbfd722d22fe4a7549.2.llvm.5971120963962824495+0x48>
 13c36f5:	48 89 cf             	mov    %rcx,%rdi
 13c36f8:	ff 15 d2 77 58 02    	call   *0x25877d2(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 13c36fe:	48 8d 15 c3 4d 4f 02 	lea    0x24f4dc3(%rip),%rdx        # 38b84c8 <anon.f07db1e3109bdebbfd722d22fe4a7549.2.llvm.5971120963962824495+0x30>
 13c3705:	48 89 cf             	mov    %rcx,%rdi
 13c3708:	ff 15 c2 77 58 02    	call   *0x25877c2(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 13c370e:	48 8d 15 9b 4d 4f 02 	lea    0x24f4d9b(%rip),%rdx        # 38b84b0 <anon.f07db1e3109bdebbfd722d22fe4a7549.2.llvm.5971120963962824495+0x18>
 13c3715:	48 89 cf             	mov    %rcx,%rdi
 13c3718:	ff 15 b2 77 58 02    	call   *0x25877b2(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 13c371e:	48 8d 15 d3 4d 4f 02 	lea    0x24f4dd3(%rip),%rdx        # 38b84f8 <anon.f07db1e3109bdebbfd722d22fe4a7549.2.llvm.5971120963962824495+0x60>
 13c3725:	4c 89 df             	mov    %r11,%rdi
 13c3728:	48 89 de             	mov    %rbx,%rsi
 13c372b:	ff 15 9f 77 58 02    	call   *0x258779f(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 13c3731:	48 8d 15 c0 4d 4f 02 	lea    0x24f4dc0(%rip),%rdx        # 38b84f8 <anon.f07db1e3109bdebbfd722d22fe4a7549.2.llvm.5971120963962824495+0x60>
 13c3738:	4c 89 d7             	mov    %r10,%rdi
 13c373b:	48 89 de             	mov    %rbx,%rsi
 13c373e:	ff 15 8c 77 58 02    	call   *0x258778c(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
